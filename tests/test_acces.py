"""RG2 : fonctions client pour les connectés, fonctions admin pour les admins."""

import pytest

from kampusbank.domaine.exceptions import AccesRefuseError, NonConnecteError
from kampusbank.service.administration import ServiceAdministration
from kampusbank.service.authentification import ServiceAuthentification
from kampusbank.service.profil import ServiceProfil
from tests.saisies import MOT_DE_PASSE_VALIDE, donnees_valides


@pytest.fixture(autouse=True)
def un_client_et_un_admin(auth: ServiceAuthentification) -> None:
    auth.inscrire(donnees_valides(), MOT_DE_PASSE_VALIDE)
    auth.creer_administrateur_initial(
        donnees_valides(email="admin@kampusbank.fr"), MOT_DE_PASSE_VALIDE
    )


def test_fonction_client_refusee_sans_connexion(profil: ServiceProfil) -> None:
    with pytest.raises(NonConnecteError):
        profil.consulter()


def test_fonction_client_refusee_apres_deconnexion(
    auth: ServiceAuthentification, profil: ServiceProfil
) -> None:
    auth.connecter("alice@exemple.fr", MOT_DE_PASSE_VALIDE)
    auth.deconnecter()

    with pytest.raises(NonConnecteError):
        profil.consulter()


def test_fonction_admin_refusee_sans_connexion(
    administration: ServiceAdministration,
) -> None:
    with pytest.raises(NonConnecteError):
        administration.lister_clients()


def test_fonction_admin_refusee_a_un_client(
    auth: ServiceAuthentification, administration: ServiceAdministration
) -> None:
    auth.connecter("alice@exemple.fr", MOT_DE_PASSE_VALIDE)

    with pytest.raises(AccesRefuseError):
        administration.lister_clients()


def test_fonction_admin_accessible_a_un_admin(
    auth: ServiceAuthentification, administration: ServiceAdministration
) -> None:
    auth.connecter("admin@kampusbank.fr", MOT_DE_PASSE_VALIDE)

    assert [c.email for c in administration.lister_clients()] == ["alice@exemple.fr"]
