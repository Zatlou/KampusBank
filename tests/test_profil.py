import pytest

from kampusbank.domaine.exceptions import EmailDejaUtiliseError, TelephoneInvalideError
from kampusbank.persistance.depot_json import DepotJson
from kampusbank.service.authentification import ServiceAuthentification
from kampusbank.service.profil import ServiceProfil
from tests.saisies import MOT_DE_PASSE_VALIDE, donnees_valides


@pytest.fixture(autouse=True)
def alice_connectee(auth: ServiceAuthentification) -> None:
    auth.inscrire(donnees_valides(), MOT_DE_PASSE_VALIDE)
    auth.inscrire(
        donnees_valides(email="bob@exemple.fr", prenom="Bob"), MOT_DE_PASSE_VALIDE
    )
    auth.connecter("alice@exemple.fr", MOT_DE_PASSE_VALIDE)


def test_modification_enregistree(profil: ServiceProfil, depot: DepotJson) -> None:
    profil.modifier(donnees_valides(nom="Martin", telephone="0700000000"))

    relu = depot.trouver_utilisateur_par_email("alice@exemple.fr")
    assert relu is not None
    assert relu.nom == "Martin"
    assert relu.telephone == "0700000000"


def test_garder_son_propre_email_est_autorise(profil: ServiceProfil) -> None:
    assert profil.modifier(donnees_valides(nom="Martin")).email == "alice@exemple.fr"


def test_rg14_prendre_l_email_d_un_autre_est_refuse(profil: ServiceProfil) -> None:
    with pytest.raises(EmailDejaUtiliseError):
        profil.modifier(donnees_valides(email="bob@exemple.fr"))


def test_rg15_telephone_invalide_rien_n_est_modifie(
    profil: ServiceProfil, depot: DepotJson
) -> None:
    with pytest.raises(TelephoneInvalideError):
        profil.modifier(donnees_valides(nom="Martin", telephone="12"))

    assert profil.consulter().nom == "Durand"
    relu = depot.trouver_utilisateur_par_email("alice@exemple.fr")
    assert relu is not None
    assert relu.nom == "Durand"
