"""Transactions : chaque opération réussie laisse une trace immuable (RG12)."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum

from kampusbank.domaine.validation import valider_montant


class TypeTransaction(Enum):
    """Nature d'une opération inscrite à l'historique."""

    DEPOT = "DEPOT"
    RETRAIT = "RETRAIT"
    VIREMENT_EMIS = "VIREMENT_EMIS"
    VIREMENT_RECU = "VIREMENT_RECU"
    ANNULATION = "ANNULATION"

    @property
    def libelle(self) -> str:
        """Nom de l'opération, pour l'affichage."""
        return _LIBELLES[self]


_LIBELLES = {
    TypeTransaction.DEPOT: "Dépôt",
    TypeTransaction.RETRAIT: "Retrait",
    TypeTransaction.VIREMENT_EMIS: "Virement émis",
    TypeTransaction.VIREMENT_RECU: "Virement reçu",
    TypeTransaction.ANNULATION: "Annulation",
}

_EST_UN_CREDIT = {
    TypeTransaction.DEPOT: True,
    TypeTransaction.VIREMENT_RECU: True,
    TypeTransaction.RETRAIT: False,
    TypeTransaction.VIREMENT_EMIS: False,
}


@dataclass(frozen=True)
class Transaction:
    """Opération inscrite à l'historique ; elle ne peut plus être modifiée.

    Un virement produit deux transactions : VIREMENT_EMIS dans l'historique du
    compte source, VIREMENT_RECU dans celui du compte destinataire (RG11).
    """

    id: int
    compte_source_id: int | None
    compte_destinataire_id: int | None
    type: TypeTransaction
    montant: Decimal
    date: datetime
    libelle: str = ""

    def __post_init__(self) -> None:
        valider_montant(self.montant)
        if self._compte_concerne() is None:
            raise ValueError(f"La transaction {self.id} ne concerne aucun compte.")

    @property
    def est_credit(self) -> bool:
        """Vrai si l'opération augmente le solde du compte concerné."""
        if self.type in _EST_UN_CREDIT:
            return _EST_UN_CREDIT[self.type]
        return self.compte_destinataire_id is not None

    @property
    def compte_concerne_id(self) -> int:
        """Compte dont l'historique contient cette ligne."""
        compte = self._compte_concerne()
        assert compte is not None
        return compte

    def _compte_concerne(self) -> int | None:
        if self.est_credit:
            return self.compte_destinataire_id
        return self.compte_source_id
