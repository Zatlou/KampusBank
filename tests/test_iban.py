"""RG4 : format de l'IBAN KampusBank."""

import random
import re

import pytest

from kampusbank.domaine.exceptions import IbanInvalideError
from kampusbank.domaine.iban import generer_iban, normaliser_iban

FORMAT_OFFICIEL = re.compile(r"FR76-KPBK-\d{4}-\d{4}-\d{4}-\d{4}-\d{3}")


def test_iban_genere_au_format_officiel() -> None:
    hasard = random.Random(1)
    for _ in range(50):
        assert FORMAT_OFFICIEL.fullmatch(generer_iban(hasard))


def test_tirages_differents() -> None:
    hasard = random.Random(2)
    assert len({generer_iban(hasard) for _ in range(100)}) == 100


@pytest.mark.parametrize(
    "saisie",
    [
        "FR76-KPBK-1234-5678-9012-3456-789",
        "fr76kpbk1234567890123456789",
        "FR76 KPBK 1234 5678 9012 3456 789",
    ],
)
def test_saisie_remise_en_forme(saisie: str) -> None:
    assert normaliser_iban(saisie) == "FR76-KPBK-1234-5678-9012-3456-789"


@pytest.mark.parametrize(
    "saisie", ["", "FR76-KPBK-1234", "FR76-AAAA-1234-5678-9012-3456-789"]
)
def test_iban_mal_forme_refuse(saisie: str) -> None:
    with pytest.raises(IbanInvalideError):
        normaliser_iban(saisie)
