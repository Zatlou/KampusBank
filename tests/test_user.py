from datetime import date, datetime, timedelta

import pytest

from kampusbank.domaine.exceptions import EmailInvalideError, TelephoneInvalideError
from tests.fabriques import utilisateur_valide

T0 = datetime(2026, 11, 23, 10, 0)
QUINZE_MINUTES = timedelta(minutes=15)


def test_un_utilisateur_n_est_pas_admin_par_defaut() -> None:
    assert utilisateur_valide().admin is False


def test_creation_refusee_si_email_invalide() -> None:
    with pytest.raises(EmailInvalideError):
        utilisateur_valide(email="pas-un-email")


def test_modification_invalide_ne_change_rien() -> None:
    utilisateur = utilisateur_valide()

    with pytest.raises(TelephoneInvalideError):
        utilisateur.modifier_informations(
            nom="Martin",
            prenom="Bob",
            email="bob@exemple.fr",
            telephone="123",
            adresse="2 rue de Lyon",
            date_naissance=date(1990, 1, 1),
        )

    assert utilisateur.nom == "Durand"
    assert utilisateur.email == "alice@exemple.fr"


class TestRG3Blocage:
    def test_quatre_echecs_ne_bloquent_pas(self) -> None:
        utilisateur = utilisateur_valide()
        for _ in range(4):
            utilisateur.enregistrer_echec_connexion(T0, 5, QUINZE_MINUTES)

        assert utilisateur.fin_de_blocage(T0) is None

    def test_cinquieme_echec_bloque_quinze_minutes(self) -> None:
        utilisateur = utilisateur_valide()
        for _ in range(5):
            utilisateur.enregistrer_echec_connexion(T0, 5, QUINZE_MINUTES)

        assert utilisateur.fin_de_blocage(T0) == T0 + QUINZE_MINUTES
        assert utilisateur.fin_de_blocage(T0 + timedelta(minutes=14)) is not None
        assert utilisateur.fin_de_blocage(T0 + QUINZE_MINUTES) is None

    def test_apres_un_blocage_le_compteur_repart_de_zero(self) -> None:
        utilisateur = utilisateur_valide()
        for _ in range(5):
            utilisateur.enregistrer_echec_connexion(T0, 5, QUINZE_MINUTES)

        plus_tard = T0 + QUINZE_MINUTES
        utilisateur.enregistrer_echec_connexion(plus_tard, 5, QUINZE_MINUTES)

        assert utilisateur.echecs_connexion == 1
        assert utilisateur.fin_de_blocage(plus_tard) is None

    def test_reinitialisation_apres_connexion_reussie(self) -> None:
        utilisateur = utilisateur_valide()
        for _ in range(3):
            utilisateur.enregistrer_echec_connexion(T0, 5, QUINZE_MINUTES)

        utilisateur.reinitialiser_echecs_connexion()

        assert utilisateur.echecs_connexion == 0
