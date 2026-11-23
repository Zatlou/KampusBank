from datetime import datetime, timedelta
from pathlib import Path

import pytest

from kampusbank.persistance.depot_json import DepotJson
from tests.fabriques import utilisateur_valide

QUINZE_MINUTES = timedelta(minutes=15)


@pytest.fixture
def fichier_donnees(tmp_path: Path) -> Path:
    return tmp_path / "donnees.json"


def test_fichier_absent_donne_un_depot_vide(fichier_donnees: Path) -> None:
    depot = DepotJson(fichier_donnees)

    assert depot.lister_utilisateurs() == []
    assert not fichier_donnees.exists()


def test_les_identifiants_ne_sont_jamais_reattribues(fichier_donnees: Path) -> None:
    depot = DepotJson(fichier_donnees)
    premier = depot.prochain_id_utilisateur()
    second = depot.prochain_id_utilisateur()

    assert second == premier + 1
    assert DepotJson(fichier_donnees).prochain_id_utilisateur() == second + 1


def test_un_utilisateur_survit_a_la_relecture_du_fichier(fichier_donnees: Path) -> None:
    utilisateur = utilisateur_valide()
    utilisateur.enregistrer_echec_connexion(
        datetime(2026, 11, 23, 10, 0), 1, QUINZE_MINUTES
    )
    DepotJson(fichier_donnees).enregistrer_utilisateur(utilisateur)

    relu = DepotJson(fichier_donnees).trouver_utilisateur_par_email("alice@exemple.fr")

    assert relu is not None
    assert relu.id == utilisateur.id
    assert relu.date_naissance == utilisateur.date_naissance
    assert relu.bloque_jusqu_a == utilisateur.bloque_jusqu_a


def test_enregistrer_deux_fois_remplace_au_lieu_de_dupliquer(
    fichier_donnees: Path,
) -> None:
    depot = DepotJson(fichier_donnees)
    utilisateur = utilisateur_valide()
    depot.enregistrer_utilisateur(utilisateur)
    utilisateur.reinitialiser_echecs_connexion()
    depot.enregistrer_utilisateur(utilisateur)

    assert len(depot.lister_utilisateurs()) == 1


def test_les_objets_renvoyes_sont_des_copies(fichier_donnees: Path) -> None:
    depot = DepotJson(fichier_donnees)
    depot.enregistrer_utilisateur(utilisateur_valide())

    copie = depot.trouver_utilisateur_par_email("alice@exemple.fr")
    assert copie is not None
    copie.enregistrer_echec_connexion(datetime(2026, 11, 23), 5, QUINZE_MINUTES)

    relu = depot.trouver_utilisateur_par_email("alice@exemple.fr")
    assert relu is not None
    assert relu.echecs_connexion == 0


def test_aucun_fichier_temporaire_ne_reste(fichier_donnees: Path) -> None:
    DepotJson(fichier_donnees).enregistrer_utilisateur(utilisateur_valide())

    assert [f.name for f in fichier_donnees.parent.iterdir()] == [fichier_donnees.name]
