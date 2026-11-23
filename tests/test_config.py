from decimal import Decimal
from pathlib import Path

from kampusbank.config.parametres import charger_parametres

RACINE_PROJET = Path(__file__).resolve().parents[1]

CONTENU_TEST = """
[persistance]
type = "json"
fichier = "data/test.json"

[administrateur]
email = "root@test.fr"
mot_de_passe = "Secret123"
nom = "Root"
prenom = "Test"
telephone = "0102030405"
adresse = "1 rue du Test"
date_naissance = "02/03/1995"

[securite]
echecs_max = 3
duree_blocage_minutes = 10
cout_bcrypt = 4

[operations]
montant_minimum = "1.00"
retrait_maximum = "500.00"
"""


def test_charge_les_parametres_types(tmp_path: Path) -> None:
    chemin = tmp_path / "kampusbank.toml"
    chemin.write_text(CONTENU_TEST, encoding="utf-8")

    parametres = charger_parametres(chemin)

    assert parametres.persistance.type == "json"
    assert parametres.administrateur.email == "root@test.fr"
    assert parametres.securite.echecs_max == 3
    assert parametres.securite.duree_blocage_minutes == 10
    assert parametres.securite.cout_bcrypt == 4
    assert parametres.administrateur.date_naissance == "02/03/1995"
    assert parametres.operations.retrait_maximum == Decimal("500.00")


def test_fichier_de_donnees_relatif_au_fichier_de_config(tmp_path: Path) -> None:
    chemin = tmp_path / "kampusbank.toml"
    chemin.write_text(CONTENU_TEST, encoding="utf-8")

    parametres = charger_parametres(chemin)

    assert parametres.persistance.fichier == tmp_path / "data" / "test.json"


def test_le_fichier_livre_avec_le_projet_est_valide() -> None:
    parametres = charger_parametres(RACINE_PROJET / "kampusbank.toml")

    assert parametres.persistance.type in {"json", "mysql"}
    assert parametres.securite.echecs_max == 5
    assert parametres.securite.duree_blocage_minutes == 15
