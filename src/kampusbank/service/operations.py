"""Opérations bancaires et historique du client connecté (RG7 à RG12, RG17)."""

from collections.abc import Callable
from datetime import datetime
from decimal import Decimal

from kampusbank.domaine.comptes import CompteBancaire
from kampusbank.domaine.exceptions import (
    CompteIntrouvableError,
    DateInvalideError,
    DonneeInvalideError,
    LimiteOperationError,
    VirementInvalideError,
)
from kampusbank.domaine.historique import FiltreHistorique
from kampusbank.domaine.iban import normaliser_iban
from kampusbank.domaine.transaction import Transaction, TypeTransaction
from kampusbank.domaine.validation import (
    formater_montant,
    lire_date_facultative,
    lire_montant,
)
from kampusbank.persistance.depot import Depot
from kampusbank.service.proprietaire import compte_du_client
from kampusbank.service.session import Session


class ServiceOperations:
    """Dépôts, retraits, virements et historique.

    Les montants arrivent en texte, tels que saisis : ils sont convertis et
    validés ici (RG17), jamais dans l'interface. Les limites (1,00 € minimum,
    1 000,00 € par retrait) viennent de la configuration.
    """

    def __init__(
        self,
        depot: Depot,
        session: Session,
        montant_minimum: Decimal,
        retrait_maximum: Decimal,
        horloge: Callable[[], datetime],
    ) -> None:
        self._depot = depot
        self._session = session
        self._montant_minimum = montant_minimum
        self._retrait_maximum = retrait_maximum
        self._horloge = horloge

    def deposer(self, compte_id: int, montant: str, libelle: str = "") -> Transaction:
        """RG8 : dépôt d'au moins 1,00 € sur un compte actif."""
        compte = self._mon_compte(compte_id)
        somme = self._lire_montant(montant)
        compte.crediter(somme)
        depot = self._transaction(TypeTransaction.DEPOT, None, compte, somme, libelle)
        self._depot.enregistrer_operation([compte], [depot])
        return depot

    def retirer(self, compte_id: int, montant: str, libelle: str = "") -> Transaction:
        """RG9 : retrait de 1,00 € à 1 000,00 €, sans rendre le solde négatif."""
        compte = self._mon_compte(compte_id)
        somme = self._lire_montant(montant)
        if somme > self._retrait_maximum:
            plafond = formater_montant(self._retrait_maximum)
            raise LimiteOperationError(f"Un retrait ne peut pas dépasser {plafond}.")
        compte.retirer(somme)
        retrait = self._transaction(
            TypeTransaction.RETRAIT, compte, None, somme, libelle
        )
        self._depot.enregistrer_operation([compte], [retrait])
        return retrait

    def virer_entre_mes_comptes(
        self, source_id: int, destination_id: int, montant: str, libelle: str = ""
    ) -> Transaction:
        """RG10 : virement entre deux comptes du client connecté."""
        source = self._mon_compte(source_id)
        destination = self._mon_compte(destination_id)
        return self._virer(source, destination, montant, libelle)

    def virer_vers_iban(
        self, source_id: int, iban: str, montant: str, libelle: str = ""
    ) -> Transaction:
        """RG10 : virement vers tout compte KampusBank, désigné par son IBAN."""
        source = self._mon_compte(source_id)
        destination = self._depot.trouver_compte_par_iban(normaliser_iban(iban))
        if destination is None:
            raise CompteIntrouvableError("Aucun compte KampusBank ne porte cet IBAN.")
        return self._virer(source, destination, montant, libelle)

    def types_operation(self) -> list[tuple[str, str]]:
        """Renvoie (code, libellé) de chaque type d'opération, pour le filtre."""
        return [(t.value, t.libelle) for t in TypeTransaction]

    def historique(
        self,
        compte_id: int | None = None,
        type_operation: str = "",
        du: str = "",
        au: str = "",
    ) -> list[Transaction]:
        """Historique filtré des comptes du client, du plus récent au plus ancien.

        Sans compte précisé, toutes les opérations de tous ses comptes sont
        prises en compte. Les dates sont au format JJ/MM/AAAA, bornes incluses.
        """
        client = self._session.exiger_connexion()
        if compte_id is None:
            comptes = frozenset(c.id for c in self._depot.lister_comptes(client.id))
        else:
            comptes = frozenset({compte_du_client(self._depot, client, compte_id).id})
        debut, fin = lire_date_facultative(du), lire_date_facultative(au)
        if debut and fin and debut > fin:
            raise DateInvalideError("La date de début doit précéder la date de fin.")
        filtre = FiltreHistorique(comptes, _lire_type(type_operation), debut, fin)
        transactions = self._depot.lister_transactions(filtre)
        return sorted(transactions, key=lambda t: (t.date, t.id), reverse=True)

    def _virer(
        self,
        source: CompteBancaire,
        destination: CompteBancaire,
        montant: str,
        libelle: str,
    ) -> Transaction:
        """RG11 : tout est vérifié avant de toucher aux soldes, puis écrit d'un bloc."""
        if source.id == destination.id:
            raise VirementInvalideError("Le compte destinataire doit être différent.")
        somme = self._lire_montant(montant)
        source.verifier_debit(somme)
        destination.verifier_credit(somme)

        source.debiter(somme)
        destination.crediter(somme)
        emis = self._transaction(
            TypeTransaction.VIREMENT_EMIS, source, destination, somme, libelle
        )
        recu = self._transaction(
            TypeTransaction.VIREMENT_RECU, source, destination, somme, libelle
        )
        self._depot.enregistrer_operation([source, destination], [emis, recu])
        return emis

    def _mon_compte(self, compte_id: int) -> CompteBancaire:
        client = self._session.exiger_connexion()
        return compte_du_client(self._depot, client, compte_id)

    def _lire_montant(self, montant: str) -> Decimal:
        somme = lire_montant(montant)
        if somme < self._montant_minimum:
            raise LimiteOperationError(
                f"Le montant minimum est de {formater_montant(self._montant_minimum)}."
            )
        return somme

    def _transaction(
        self,
        type_operation: TypeTransaction,
        source: CompteBancaire | None,
        destination: CompteBancaire | None,
        montant: Decimal,
        libelle: str,
    ) -> Transaction:
        return Transaction(
            id=self._depot.prochain_id_transaction(),
            compte_source_id=source.id if source else None,
            compte_destinataire_id=destination.id if destination else None,
            type=type_operation,
            montant=montant,
            date=self._horloge(),
            libelle=libelle.strip(),
        )


def _lire_type(code: str) -> TypeTransaction | None:
    if not code:
        return None
    try:
        return TypeTransaction(code)
    except ValueError:
        raise DonneeInvalideError(f"Type d'opération inconnu : « {code} ».") from None
