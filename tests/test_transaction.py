"""Transactions immuables (RG12) et filtres de l'historique."""

import dataclasses
from datetime import date, datetime
from decimal import Decimal

import pytest

from kampusbank.domaine.exceptions import MontantInvalideError
from kampusbank.domaine.historique import FiltreHistorique
from kampusbank.domaine.transaction import Transaction, TypeTransaction


def transaction(
    type_operation: TypeTransaction,
    source: int | None,
    destination: int | None,
    jour: int = 10,
    montant: str = "10.00",
) -> Transaction:
    return Transaction(
        id=1,
        compte_source_id=source,
        compte_destinataire_id=destination,
        type=type_operation,
        montant=Decimal(montant),
        date=datetime(2026, 11, jour, 12, 0),
    )


def test_une_transaction_est_immuable() -> None:
    depot = transaction(TypeTransaction.DEPOT, None, 1)
    with pytest.raises(dataclasses.FrozenInstanceError):
        depot.montant = Decimal("999.00")  # type: ignore[misc]


@pytest.mark.parametrize("montant", ["0", "-5.00", "10.001"])
def test_rg17_montant_invalide_refuse(montant: str) -> None:
    with pytest.raises(MontantInvalideError):
        transaction(TypeTransaction.DEPOT, None, 1, montant=montant)


@pytest.mark.parametrize(
    ("type_operation", "source", "destination", "credit", "concerne"),
    [
        (TypeTransaction.DEPOT, None, 1, True, 1),
        (TypeTransaction.RETRAIT, 1, None, False, 1),
        (TypeTransaction.VIREMENT_EMIS, 1, 2, False, 1),
        (TypeTransaction.VIREMENT_RECU, 1, 2, True, 2),
    ],
)
def test_sens_et_compte_concerne(
    type_operation: TypeTransaction,
    source: int | None,
    destination: int | None,
    credit: bool,
    concerne: int,
) -> None:
    ligne = transaction(type_operation, source, destination)
    assert ligne.est_credit is credit
    assert ligne.compte_concerne_id == concerne


class TestFiltreHistorique:
    def test_filtre_par_compte(self) -> None:
        filtre = FiltreHistorique(frozenset({2}))
        assert filtre.accepte(transaction(TypeTransaction.VIREMENT_RECU, 1, 2))
        assert not filtre.accepte(transaction(TypeTransaction.VIREMENT_EMIS, 1, 2))

    def test_filtre_par_type(self) -> None:
        filtre = FiltreHistorique(frozenset({1}), type=TypeTransaction.RETRAIT)
        assert filtre.accepte(transaction(TypeTransaction.RETRAIT, 1, None))
        assert not filtre.accepte(transaction(TypeTransaction.DEPOT, None, 1))

    def test_periode_bornes_incluses(self) -> None:
        filtre = FiltreHistorique(
            frozenset({1}), du=date(2026, 11, 10), au=date(2026, 11, 12)
        )
        jours_acceptes = [
            jour
            for jour in range(8, 15)
            if filtre.accepte(transaction(TypeTransaction.DEPOT, None, 1, jour))
        ]
        assert jours_acceptes == [10, 11, 12]
