"""EC1 et EC8 : chaque couche n'importe que ce qu'elle a le droit d'importer."""

import ast
from pathlib import Path

PAQUET = Path(__file__).resolve().parents[1] / "src" / "kampusbank"


def _imports_de(couche: str) -> set[str]:
    modules: set[str] = set()
    for fichier in (PAQUET / couche).rglob("*.py"):
        arbre = ast.parse(fichier.read_text(encoding="utf-8"))
        for noeud in ast.walk(arbre):
            if isinstance(noeud, ast.Import):
                modules.update(alias.name for alias in noeud.names)
            elif isinstance(noeud, ast.ImportFrom) and noeud.module:
                modules.add(noeud.module)
    return modules


def _violations(couche: str, interdits: list[str]) -> set[str]:
    return {
        module
        for module in _imports_de(couche)
        for interdit in interdits
        if module == interdit or module.startswith(interdit + ".")
    }


def test_le_domaine_ne_depend_d_aucune_autre_couche() -> None:
    interdits = [
        "tkinter",
        "json",
        "kampusbank.service",
        "kampusbank.persistance",
        "kampusbank.ihm",
        "kampusbank.config",
    ]
    assert _violations("domaine", interdits) == set()


def test_les_services_ignorent_l_interface_et_le_json() -> None:
    assert _violations("service", ["tkinter", "json", "kampusbank.ihm"]) == set()


def test_l_interface_ne_passe_que_par_les_services() -> None:
    interdits = ["json", "bcrypt", "kampusbank.persistance", "kampusbank.config"]
    assert _violations("ihm", interdits) == set()
