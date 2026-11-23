from datetime import date

import pytest

from kampusbank.domaine.exceptions import (
    ChampObligatoireError,
    DateInvalideError,
    DonneeInvalideError,
    EmailInvalideError,
    KampusBankError,
    MotDePasseInvalideError,
    TelephoneInvalideError,
)
from kampusbank.domaine.validation import (
    formater_date,
    lire_date,
    valider_email,
    valider_mot_de_passe,
    valider_obligatoire,
    valider_telephone,
)


def test_toutes_les_erreurs_de_saisie_derivent_de_kampusbankerror() -> None:
    assert issubclass(DonneeInvalideError, KampusBankError)
    assert issubclass(EmailInvalideError, DonneeInvalideError)


class TestRG14Email:
    def test_email_valide_normalise(self) -> None:
        assert valider_email("  Alice.Durand@Exemple.FR ") == "alice.durand@exemple.fr"

    @pytest.mark.parametrize(
        "email",
        ["", "alice", "alice@", "@exemple.fr", "alice@exemple", "a lice@exemple.fr"],
    )
    def test_email_mal_forme_refuse(self, email: str) -> None:
        with pytest.raises(EmailInvalideError):
            valider_email(email)


class TestRG15Telephone:
    def test_dix_chiffres_acceptes(self) -> None:
        assert valider_telephone("0612345678") == "0612345678"

    def test_espaces_toleres_a_la_saisie(self) -> None:
        assert valider_telephone("06 12 34 56 78") == "0612345678"

    @pytest.mark.parametrize(
        "telephone", ["061234567", "06123456789", "06123456ab", ""]
    )
    def test_autre_que_dix_chiffres_refuse(self, telephone: str) -> None:
        with pytest.raises(TelephoneInvalideError):
            valider_telephone(telephone)


class TestRG16MotDePasse:
    def test_mot_de_passe_conforme(self) -> None:
        assert valider_mot_de_passe("Secret123") == "Secret123"

    @pytest.mark.parametrize(
        "mot_de_passe",
        [
            "Sec123",  # moins de 8 caractères
            "secret123",  # pas de majuscule
            "SecretSecret",  # pas de chiffre
            "A1" + "x" * 80,  # au-delà de la limite de bcrypt
        ],
    )
    def test_mot_de_passe_faible_refuse(self, mot_de_passe: str) -> None:
        with pytest.raises(MotDePasseInvalideError):
            valider_mot_de_passe(mot_de_passe)


class TestChampsEtDates:
    def test_champ_obligatoire_vide_refuse(self) -> None:
        with pytest.raises(ChampObligatoireError):
            valider_obligatoire("   ", "nom")

    def test_champ_obligatoire_nettoye(self) -> None:
        assert valider_obligatoire("  Durand ", "nom") == "Durand"

    def test_date_lue_au_format_francais(self) -> None:
        assert lire_date("15/04/2001") == date(2001, 4, 15)

    @pytest.mark.parametrize("texte", ["2001-04-15", "31/02/2001", "demain", ""])
    def test_date_invalide_refusee(self, texte: str) -> None:
        with pytest.raises(DateInvalideError):
            lire_date(texte)

    def test_formater_puis_lire_redonne_la_meme_date(self) -> None:
        assert lire_date(formater_date(date(1999, 12, 31))) == date(1999, 12, 31)
