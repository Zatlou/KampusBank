"""RG17 : montants positifs, 2 décimales au plus, toujours en Decimal."""

from decimal import Decimal

import pytest

from kampusbank.domaine.exceptions import MontantInvalideError
from kampusbank.domaine.validation import (
    formater_montant,
    lire_montant,
    valider_montant,
)


@pytest.mark.parametrize(
    ("saisie", "attendu"),
    [
        ("12", "12.00"),
        ("12,5", "12.50"),
        ("12.50", "12.50"),
        ("1 250,75", "1250.75"),
    ],
)
def test_saisies_acceptees(saisie: str, attendu: str) -> None:
    assert lire_montant(saisie) == Decimal(attendu)


@pytest.mark.parametrize(
    "saisie", ["", "abc", "-5", "0", "0,00", "12,345", "1e3", "NaN", "12,5,0"]
)
def test_saisies_refusees(saisie: str) -> None:
    with pytest.raises(MontantInvalideError):
        lire_montant(saisie)


def test_trois_decimales_refusees_meme_en_decimal() -> None:
    with pytest.raises(MontantInvalideError):
        valider_montant(Decimal("10.001"))


def test_pas_d_erreur_d_arrondi_contrairement_aux_float() -> None:
    assert 0.1 + 0.2 != 0.3
    assert lire_montant("0,10") + lire_montant("0,20") == Decimal("0.30")


def test_affichage_a_la_francaise() -> None:
    assert formater_montant(Decimal("1250.5")) == "1 250,50 €"
