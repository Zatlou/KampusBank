"""Fonctions réservées aux administrateurs (complétées au jalon 3)."""

from kampusbank.domaine.user import User
from kampusbank.persistance.depot import Depot
from kampusbank.service.session import Session


class ServiceAdministration:
    """Supervision des clients ; chaque méthode exige un administrateur (RG2)."""

    def __init__(self, depot: Depot, session: Session) -> None:
        self._depot = depot
        self._session = session

    def lister_clients(self) -> list[User]:
        """Renvoie tous les clients, sans les administrateurs."""
        self._session.exiger_admin()
        return [u for u in self._depot.lister_utilisateurs() if not u.admin]
