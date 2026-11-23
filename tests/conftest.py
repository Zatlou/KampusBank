"""Fixtures pytest : objets neufs et fichier temporaire pour chaque test (EC9)."""

import random
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from kampusbank.domaine.iban import generer_iban
from kampusbank.domaine.user import User
from kampusbank.persistance.depot_json import DepotJson
from kampusbank.service.administration import ServiceAdministration
from kampusbank.service.authentification import ServiceAuthentification
from kampusbank.service.comptes import ServiceComptes
from kampusbank.service.hachage import HacheurMotDePasse
from kampusbank.service.operations import ServiceOperations
from kampusbank.service.profil import ServiceProfil
from kampusbank.service.session import Session
from tests.fabriques import DUREE_BLOCAGE_MINUTES, ECHECS_MAX, HorlogeFactice
from tests.saisies import MOT_DE_PASSE_VALIDE, donnees_valides


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
def administration(
    depot: DepotJson, session: Session, horloge: HorlogeFactice
) -> ServiceAdministration:
    return ServiceAdministration(depot, session, horloge)


@pytest.fixture
def comptes(
    depot: DepotJson, session: Session, horloge: HorlogeFactice
) -> ServiceComptes:
    hasard = random.Random(0)
    return ServiceComptes(depot, session, lambda: generer_iban(hasard), horloge)


@pytest.fixture
def operations(
    depot: DepotJson, session: Session, horloge: HorlogeFactice
) -> ServiceOperations:
    return ServiceOperations(
        depot,
        session,
        montant_minimum=Decimal("1.00"),
        retrait_maximum=Decimal("1000.00"),
        horloge=horloge,
    )


@pytest.fixture
def alice(auth: ServiceAuthentification) -> User:
    """Cliente inscrite et connectée."""
    auth.inscrire(donnees_valides(), MOT_DE_PASSE_VALIDE)
    return auth.connecter("alice@exemple.fr", MOT_DE_PASSE_VALIDE)
