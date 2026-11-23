"""Session : l'utilisateur actuellement connecté (un seul à la fois)."""

from kampusbank.domaine.exceptions import AccesRefuseError, NonConnecteError
from kampusbank.domaine.user import User


class Session:
    """Garde l'utilisateur connecté et contrôle les accès (RG2)."""

    def __init__(self) -> None:
        self._utilisateur: User | None = None

    @property
    def utilisateur(self) -> User | None:
        """Utilisateur connecté, ou None."""
        return self._utilisateur

    def ouvrir(self, utilisateur: User) -> None:
        """Connecte l'utilisateur (remplace la session précédente)."""
        self._utilisateur = utilisateur

    def fermer(self) -> None:
        """Déconnecte l'utilisateur."""
        self._utilisateur = None

    def exiger_connexion(self) -> User:
        """Renvoie l'utilisateur connecté, ou lève NonConnecteError."""
        if self._utilisateur is None:
            raise NonConnecteError(
                "Vous devez être connecté pour accéder à cette fonction."
            )
        return self._utilisateur

    def exiger_admin(self) -> User:
        """Renvoie l'administrateur connecté, ou lève une erreur d'accès."""
        utilisateur = self.exiger_connexion()
        if not utilisateur.admin:
            raise AccesRefuseError("Cette fonction est réservée aux administrateurs.")
        return utilisateur
