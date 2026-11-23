"""Fixtures pytest : objets neufs et fichier temporaire pour chaque test (EC9)."""

from datetime import timedelta
from pathlib import Path

import pytest

from kampusbank.persistance.depot_json import DepotJson
from kampusbank.service.administration import ServiceAdministration
from kampusbank.service.authentification import ServiceAuthentification
from kampusbank.service.hachage import HacheurMotDePasse
from kampusbank.service.profil import ServiceProfil
from kampusbank.service.session import Session
from tests.fabriques import DUREE_BLOCAGE_MINUTES, ECHECS_MAX, HorlogeFactice


@pytest.fixture
def fichier_donnees(tmp_path: Path) -> Path:
    return tmp_path / "donnees.json"


@pytest.fixture
def depot(fichier_donnees: Path) -> DepotJson:
    return DepotJson(fichier_donnees)


@pytest.fixture
def horloge() -> HorlogeFactice:
    return HorlogeFactice()


@pytest.fixture
def session() -> Session:
    return Session()


@pytest.fixture
def hacheur() -> HacheurMotDePasse:
    return HacheurMotDePasse(cout=4)


@pytest.fixture
def auth(
    depot: DepotJson,
    hacheur: HacheurMotDePasse,
    session: Session,
    horloge: HorlogeFactice,
) -> ServiceAuthentification:
    return ServiceAuthentification(
        depot,
        hacheur,
        session,
        echecs_max=ECHECS_MAX,
        duree_blocage=timedelta(minutes=DUREE_BLOCAGE_MINUTES),
        horloge=horloge,
    )


@pytest.fixture
def profil(depot: DepotJson, session: Session) -> ServiceProfil:
    return ServiceProfil(depot, session)


@pytest.fixture
def administration(depot: DepotJson, session: Session) -> ServiceAdministration:
    return ServiceAdministration(depot, session)
