"""Contrat de la persistance : ce que les services peuvent demander (EC6)."""

from abc import ABC, abstractmethod

from kampusbank.domaine.user import User


class Depot(ABC):
    """Enregistre et relit les données de l'application.

    Les services ne connaissent que cette classe abstraite : on peut passer
    du JSON à MySQL en changeant d'implémentation, sans toucher aux services.
    Les objets renvoyés sont des copies : une modification n'est enregistrée
    qu'après un appel explicite à une méthode « enregistrer ».
    """

    @abstractmethod
    def prochain_id_utilisateur(self) -> int:
        """Réserve et renvoie un identifiant jamais attribué."""

    @abstractmethod
    def enregistrer_utilisateur(self, utilisateur: User) -> None:
        """Ajoute l'utilisateur, ou le remplace s'il existe déjà (même id)."""

    @abstractmethod
    def trouver_utilisateur_par_email(self, email: str) -> User | None:
        """Renvoie l'utilisateur qui a cet email (déjà normalisé), ou None."""

    @abstractmethod
    def lister_utilisateurs(self) -> list[User]:
        """Renvoie tous les utilisateurs, administrateurs compris."""
