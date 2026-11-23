"""Critères de filtrage de l'historique des transactions."""

from dataclasses import dataclass
from datetime import date

from kampusbank.domaine.transaction import Transaction, TypeTransaction


@dataclass(frozen=True)
class FiltreHistorique:
    """Comptes, type d'opération et période (bornes incluses) à afficher.

    Un critère à None ne filtre rien. Le filtre est transmis au dépôt : une
    base MySQL peut le traduire en clause WHERE au lieu de tout relire.
    """

    comptes_ids: frozenset[int]
    type: TypeTransaction | None = None
    du: date | None = None
    au: date | None = None

    def accepte(self, transaction: Transaction) -> bool:
        """Vrai si la transaction répond à tous les critères."""
        jour = transaction.date.date()
        return (
            transaction.compte_concerne_id in self.comptes_ids
            and (self.type is None or transaction.type is self.type)
            and (self.du is None or jour >= self.du)
            and (self.au is None or jour <= self.au)
        )
