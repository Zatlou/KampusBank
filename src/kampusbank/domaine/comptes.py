"""Comptes bancaires : une classe abstraite et ses spécialisations (EC2, EC3)."""

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import ClassVar

from kampusbank.domaine.exceptions import (
    CompteBloqueError,
    CompteNonVideError,
    PlafondDepasseError,
    RetraitInterditError,
    SoldeInsuffisantError,
    TypeCompteInconnuError,
)
from kampusbank.domaine.validation import formater_montant, valider_montant

_ZERO = Decimal("0.00")
_TYPES_DE_COMPTE: dict[str, "type[CompteBancaire]"] = {}


class StatutCompte(Enum):
    """État d'un compte : un compte bloqué n'accepte aucune opération (RG7)."""

    ACTIF = "ACTIF"
    BLOQUE = "BLOQUE"

    @property
    def libelle(self) -> str:
        """Statut pour l'affichage."""
        return "Bloqué" if self is StatutCompte.BLOQUE else "Actif"


class CompteBancaire(ABC):
    """Compte bancaire d'un client.

    Le solde est privé : il ne change que par crediter et debiter, qui
    refusent tout ce qui le rendrait négatif ou dépasserait le plafond (EC3).

    Chaque sous-classe déclare son CODE et son LIBELLE et s'inscrit d'elle-même
    dans le registre des types : ajouter un type de compte, c'est écrire une
    sous-classe, sans toucher aux services ni à l'interface (EC2).
    """

    CODE: ClassVar[str]
    LIBELLE: ClassVar[str]

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        _TYPES_DE_COMPTE[cls.CODE] = cls

    def __init__(
        self,
        *,
        id: int,
        proprietaire_id: int,
        iban: str,
        date_creation: datetime,
        solde: Decimal = _ZERO,
        statut: StatutCompte = StatutCompte.ACTIF,
    ) -> None:
        self._id = id
        self._proprietaire_id = proprietaire_id
        self._iban = iban
        self._date_creation = date_creation
        self._solde = solde
        self._statut = statut

    @property
    def id(self) -> int:
        """Identifiant unique."""
        return self._id

    @property
    def proprietaire_id(self) -> int:
        """Identifiant du client propriétaire."""
        return self._proprietaire_id

    @property
    def iban(self) -> str:
        """IBAN unique, au format FR76-KPBK-XXXX-XXXX-XXXX-XXXX-XXX."""
        return self._iban

    @property
    def libelle(self) -> str:
        """Nom du type de compte, pour l'affichage."""
        return self.LIBELLE

    @property
    def solde(self) -> Decimal:
        """Solde actuel, jamais négatif."""
        return self._solde

    @property
    def statut(self) -> StatutCompte:
        """ACTIF ou BLOQUE."""
        return self._statut

    @property
    def est_bloque(self) -> bool:
        """Vrai si le compte est bloqué (RG7)."""
        return self._statut is StatutCompte.BLOQUE

    @property
    def date_creation(self) -> datetime:
        """Date et heure d'ouverture du compte."""
        return self._date_creation

    @property
    @abstractmethod
    def plafond(self) -> Decimal | None:
        """Solde maximal autorisé, ou None si le compte n'est pas plafonné."""

    def verifier_credit(self, montant: Decimal) -> None:
        """Lève une exception si le compte ne peut pas recevoir ce montant."""
        self._exiger_actif()
        plafond = self.plafond
        if plafond is not None and self._solde + montant > plafond:
            reste = formater_montant(plafond - self._solde)
            raise PlafondDepasseError(
                f"Le {self.LIBELLE} est plafonné à {formater_montant(plafond)} : "
                f"il ne peut plus recevoir que {reste}."
            )

    def verifier_debit(self, montant: Decimal) -> None:
        """Lève une exception si ce montant ne peut pas sortir du compte."""
        self._exiger_actif()
        if montant > self._solde:
            raise SoldeInsuffisantError(
                f"Solde insuffisant : {formater_montant(self._solde)} disponibles."
            )

    def verifier_retrait(self, montant: Decimal) -> None:
        """Lève une exception si ce retrait d'espèces est impossible."""
        self.verifier_debit(montant)

    def crediter(self, montant: Decimal) -> None:
        """Ajoute le montant au solde, après toutes les vérifications."""
        montant = valider_montant(montant)
        self.verifier_credit(montant)
        self._solde += montant

    def debiter(self, montant: Decimal) -> None:
        """Retire le montant du solde ; le solde ne devient jamais négatif."""
        montant = valider_montant(montant)
        self.verifier_debit(montant)
        self._solde -= montant

    def retirer(self, montant: Decimal) -> None:
        """Retrait d'espèces : comme un débit, si le type de compte l'autorise."""
        self.verifier_retrait(montant)
        self.debiter(montant)

    def verifier_suppression(self) -> None:
        """RG6 : seul un compte à exactement 0,00 € peut être supprimé."""
        if self._solde != _ZERO:
            raise CompteNonVideError(
                "Ce compte ne peut pas être supprimé : son solde est de "
                f"{formater_montant(self._solde)} (il doit être de 0,00 €)."
            )

    def bloquer(self) -> None:
        """Bloque le compte (administrateur)."""
        self._statut = StatutCompte.BLOQUE

    def debloquer(self) -> None:
        """Débloque le compte (administrateur)."""
        self._statut = StatutCompte.ACTIF

    def _exiger_actif(self) -> None:
        if self._statut is StatutCompte.BLOQUE:
            raise CompteBloqueError(
                f"Le compte {self._iban} est bloqué : aucune opération possible."
            )

    @property
    def type(self) -> str:
        """Code du type de compte (COURANT, LIVRET_A, PEL…)."""
        return self.CODE


class CompteCourant(CompteBancaire):
    """Compte du quotidien : ni plafond ni restriction de retrait."""

    CODE = "COURANT"
    LIBELLE = "Compte courant"

    @property
    def plafond(self) -> Decimal | None:
        """Pas de plafond."""
        return None


class LivretA(CompteBancaire):
    """Livret d'épargne réglementé, plafonné à 22 950 €."""

    CODE = "LIVRET_A"
    LIBELLE = "Livret A"

    @property
    def plafond(self) -> Decimal | None:
        """Plafond réglementaire du Livret A."""
        return Decimal("22950.00")


class PEL(CompteBancaire):
    """Plan d'épargne logement : plafonné à 61 200 €, sans retrait d'espèces.

    L'argent n'en sort que par virement : sinon un PEL non vide ne pourrait
    jamais être vidé, donc jamais supprimé (RG6).
    """

    CODE = "PEL"
    LIBELLE = "PEL"

    @property
    def plafond(self) -> Decimal | None:
        """Plafond réglementaire du PEL."""
        return Decimal("61200.00")

    def verifier_retrait(self, montant: Decimal) -> None:
        """Toujours refusé : un PEL ne se vide que par virement."""
        raise RetraitInterditError(
            "Les retraits sont interdits sur un PEL : faites un virement."
        )


def types_de_compte() -> list[type[CompteBancaire]]:
    """Renvoie toutes les classes de compte inscrites, dans l'ordre de déclaration."""
    return list(_TYPES_DE_COMPTE.values())


def classe_de_compte(code: str) -> type[CompteBancaire]:
    """Renvoie la classe correspondant à un code de type (COURANT, LIVRET_A…)."""
    try:
        return _TYPES_DE_COMPTE[code]
    except KeyError:
        raise TypeCompteInconnuError(f"Type de compte inconnu : « {code} ».") from None
