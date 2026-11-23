"""RG2, RG4, RG5, RG6 côté service : comptes du client connecté."""

from datetime import datetime
from decimal import Decimal

import pytest

from kampusbank.domaine.comptes import CompteCourant
from kampusbank.domaine.exceptions import (
    CompteIntrouvableError,
    CompteNonVideError,
    NonConnecteError,
    TypeCompteInconnuError,
)
from kampusbank.domaine.user import User
from kampusbank.persistance.depot_json import DepotJson
from kampusbank.service.authentification import ServiceAuthentification
from kampusbank.service.comptes import ServiceComptes
from kampusbank.service.session import Session
from tests.fabriques import HorlogeFactice
from tests.saisies import MOT_DE_PASSE_VALIDE, donnees_valides
from tests.test_iban import FORMAT_OFFICIEL


def test_rg2_il_faut_etre_connecte(comptes: ServiceComptes) -> None:
    with pytest.raises(NonConnecteError):
        comptes.lister()


def test_ouverture_a_zero_avec_iban(comptes: ServiceComptes, alice: User) -> None:
    compte = comptes.ouvrir("LIVRET_A")

    assert compte.solde == Decimal("0.00")
    assert compte.proprietaire_id == alice.id
    assert FORMAT_OFFICIEL.fullmatch(compte.iban)


def test_rg4_un_iban_deja_pris_est_tire_a_nouveau(
    depot: DepotJson, session: Session, horloge: HorlogeFactice, alice: User
) -> None:
    tirages = iter(
        [
            "FR76-KPBK-1111-1111-1111-1111-111",
            "FR76-KPBK-1111-1111-1111-1111-111",
            "FR76-KPBK-2222-2222-2222-2222-222",
        ]
    )
    service = ServiceComptes(depot, session, lambda: next(tirages), horloge)

    premier = service.ouvrir("COURANT")
    second = service.ouvrir("COURANT")

    assert premier.iban != second.iban
    assert second.iban == "FR76-KPBK-2222-2222-2222-2222-222"


def test_rg5_plusieurs_comptes(comptes: ServiceComptes, alice: User) -> None:
    for code, _ in comptes.types_disponibles():
        comptes.ouvrir(code)

    assert sorted(c.type for c in comptes.lister()) == ["COURANT", "LIVRET_A", "PEL"]


def test_type_inconnu_refuse(comptes: ServiceComptes, alice: User) -> None:
    with pytest.raises(TypeCompteInconnuError):
        comptes.ouvrir("ASSURANCE_VIE")


def test_rg6_suppression_d_un_compte_vide(comptes: ServiceComptes, alice: User) -> None:
    compte = comptes.ouvrir("COURANT")
    comptes.supprimer(compte.id)

    assert comptes.lister() == []


def test_rg6_compte_non_vide_conserve(
    comptes: ServiceComptes, depot: DepotJson, alice: User
) -> None:
    depot.enregistrer_compte(
        CompteCourant(
            id=99,
            proprietaire_id=alice.id,
            iban="FR76-KPBK-9999-9999-9999-9999-999",
            date_creation=datetime(2026, 11, 1),
            solde=Decimal("0.01"),
        )
    )

    with pytest.raises(CompteNonVideError):
        comptes.supprimer(99)
    assert [c.id for c in comptes.lister()] == [99]


def test_on_ne_voit_pas_les_comptes_des_autres(
    comptes: ServiceComptes, auth: ServiceAuthentification, alice: User
) -> None:
    compte_alice = comptes.ouvrir("COURANT")
    auth.inscrire(donnees_valides(email="bob@exemple.fr"), MOT_DE_PASSE_VALIDE)
    auth.connecter("bob@exemple.fr", MOT_DE_PASSE_VALIDE)

    with pytest.raises(CompteIntrouvableError):
        comptes.consulter(compte_alice.id)
    with pytest.raises(CompteIntrouvableError):
        comptes.supprimer(compte_alice.id)
