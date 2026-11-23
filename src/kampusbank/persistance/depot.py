"""Contrat de la persistance : ce que les services peuvent demander (EC6)."""

from abc import ABC, abstractmethod

from kampusbank.domaine.comptes import CompteBancaire
from kampusbank.domaine.historique import FiltreHistorique
from kampusbank.domaine.transaction import Transaction
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
        """Réserve et renvoie un identifiant d'utilisateur jamais attribué."""

    @abstractmethod
    def enregistrer_utilisateur(self, utilisateur: User) -> None:
        """Ajoute l'utilisateur, ou le remplace s'il existe déjà (même id)."""

    @abstractmethod
    def trouver_utilisateur_par_email(self, email: str) -> User | None:
        """Renvoie l'utilisateur qui a cet email (déjà normalisé), ou None."""

    @abstractmethod
    def lister_utilisateurs(self) -> list[User]:
        """Renvoie tous les utilisateurs, administrateurs compris."""

    @abstractmethod
    def trouver_utilisateur(self, utilisateur_id: int) -> User | None:
        """Renvoie l'utilisateur qui a cet identifiant, ou None."""

    @abstractmethod
    def supprimer_utilisateur(self, utilisateur_id: int) -> None:
        """Supprime l'utilisateur et ses comptes ; l'historique est conservé."""

    @abstractmethod
    def prochain_id_compte(self) -> int:
        """Réserve et renvoie un identifiant de compte jamais attribué."""

    @abstractmethod
    def enregistrer_compte(self, compte: CompteBancaire) -> None:
        """Ajoute le compte, ou le remplace s'il existe déjà (même id)."""

    @abstractmethod
    def supprimer_compte(self, compte_id: int) -> None:
        """Supprime le compte ; ses transactions restent dans l'historique."""

    @abstractmethod
    def trouver_compte(self, compte_id: int) -> CompteBancaire | None:
        """Renvoie le compte qui a cet identifiant, ou None."""

    @abstractmethod
    def trouver_compte_par_iban(self, iban: str) -> CompteBancaire | None:
        """Renvoie le compte qui a cet IBAN (déjà normalisé), ou None."""

    @abstractmethod
    def lister_comptes(
        self, proprietaire_id: int | None = None
    ) -> list[CompteBancaire]:
        """Renvoie les comptes d'un client, ou tous les comptes si None."""

    @abstractmethod
    def prochain_id_transaction(self) -> int:
        """Réserve et renvoie un identifiant de transaction jamais attribué."""

    @abstractmethod
    def enregistrer_operation(
        self, comptes: list[CompteBancaire], transactions: list[Transaction]
    ) -> None:
        """Enregistre ensemble soldes modifiés et transactions (tout ou rien)."""

    @abstractmethod
    def lister_transactions(self, filtre: FiltreHistorique) -> list[Transaction]:
        """Renvoie les transactions qui répondent au filtre."""
