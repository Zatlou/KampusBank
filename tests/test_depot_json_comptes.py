"""Persistance JSON des comptes et des transactions (EC6, RG11, EC9)."""

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from kampusbank.domaine.comptes import LivretA, StatutCompte
from kampusbank.domaine.historique import FiltreHistorique
from kampusbank.domaine.transaction import Transaction, TypeTransaction
from kampusbank.persistance.depot_json import DepotJson

OUVERTURE = datetime(2026, 11, 23, 9, 30)


@pytest.fixture
def fichier_donnees(tmp_path: Path) -> Path:
    return tmp_path / "donnees.json"


def livret(solde: str = "0.10") -> LivretA:
    return LivretA(
        id=1,
        proprietaire_id=7,
        iban="FR76-KPBK-1234-5678-9012-3456-789",
        date_creation=OUVERTURE,
        solde=Decimal(solde),
    )


def depot_de(compte_id: int, montant: str) -> Transaction:
    return Transaction(
        id=1,
        compte_source_id=None,
        compte_destinataire_id=compte_id,
        type=TypeTransaction.DEPOT,
        montant=Decimal(montant),
        date=OUVERTURE,
    )


def test_un_livret_a_est_relu_en_livret_a(fichier_donnees: Path) -> None:
    DepotJson(fichier_donnees).enregistrer_compte(livret())

    relu = DepotJson(fichier_donnees).trouver_compte(1)

    assert isinstance(relu, LivretA)
    assert relu.solde == Decimal("0.10")
    assert relu.statut is StatutCompte.ACTIF
    assert relu.date_creation == OUVERTURE


def test_les_montants_sont_ecrits_en_texte(fichier_donnees: Path) -> None:
    DepotJson(fichier_donnees).enregistrer_compte(livret("1250.50"))

    contenu = json.loads(fichier_donnees.read_text(encoding="utf-8"))

    assert contenu["comptes"][0]["solde"] == "1250.50"


def test_recherche_par_iban_et_par_proprietaire(fichier_donnees: Path) -> None:
    depot = DepotJson(fichier_donnees)
    depot.enregistrer_compte(livret())

    assert depot.trouver_compte_par_iban("FR76-KPBK-1234-5678-9012-3456-789")
    assert [c.id for c in depot.lister_comptes(7)] == [1]
    assert depot.lister_comptes(8) == []


def test_operation_ecrite_d_un_seul_bloc(fichier_donnees: Path) -> None:
    depot = DepotJson(fichier_donnees)
    compte = livret("0.00")
    compte.crediter(Decimal("40.00"))
    depot.enregistrer_operation([compte], [depot_de(compte.id, "40.00")])

    relu = DepotJson(fichier_donnees)
    compte_relu = relu.trouver_compte(1)
    assert compte_relu is not None
    assert compte_relu.solde == Decimal("40.00")
    assert len(relu.lister_transactions(FiltreHistorique(frozenset({1})))) == 1


def test_rg11_une_ecriture_ratee_ne_change_rien(
    fichier_donnees: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    depot = DepotJson(fichier_donnees)
    depot.enregistrer_compte(livret("10.00"))

    def disque_plein(donnees: object) -> None:
        raise OSError("disque plein")

    monkeypatch.setattr(depot, "_ecrire", disque_plein)
    compte = livret("10.00")
    compte.crediter(Decimal("5.00"))
    with pytest.raises(OSError):
        depot.enregistrer_operation([compte], [depot_de(1, "5.00")])

    en_memoire = depot.trouver_compte(1)
    assert en_memoire is not None
    assert en_memoire.solde == Decimal("10.00")
    assert depot.lister_transactions(FiltreHistorique(frozenset({1}))) == []


def test_suppression_d_un_compte(fichier_donnees: Path) -> None:
    depot = DepotJson(fichier_donnees)
    depot.enregistrer_compte(livret())
    depot.supprimer_compte(1)

    assert depot.trouver_compte(1) is None


def test_un_fichier_du_jalon_1_reste_lisible(fichier_donnees: Path) -> None:
    ancien = {"compteurs": {"utilisateurs": 0}, "utilisateurs": []}
    fichier_donnees.write_text(json.dumps(ancien), encoding="utf-8")

    depot = DepotJson(fichier_donnees)

    assert depot.lister_comptes() == []
    assert depot.lister_transactions(FiltreHistorique(frozenset({1}))) == []
    assert depot.prochain_id_compte() == 1
