"""Fonctions réservées aux administrateurs : chacune exige un admin (RG2)."""

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from kampusbank.domaine.comptes import CompteBancaire
from kampusbank.domaine.exceptions import (
    AnnulationImpossibleError,
    ClientIntrouvableError,
    CompteIntrouvableError,
    SuppressionClientImpossibleError,
)
from kampusbank.domaine.historique import FiltreHistorique
from kampusbank.domaine.transaction import Transaction, TypeTransaction
from kampusbank.domaine.user import User
from kampusbank.domaine.validation import lire_date
from kampusbank.persistance.depot import Depot
from kampusbank.service.formulaires import DonneesPersonnelles
from kampusbank.service.session import Session
from kampusbank.service.unicite import exiger_email_disponible

_VIREMENTS = (TypeTransaction.VIREMENT_EMIS, TypeTransaction.VIREMENT_RECU)


@dataclass(frozen=True)
class Statistiques:
    """Chiffres clés de la banque."""

    nombre_clients: int
    nombre_comptes: int
    total_depots: Decimal
    total_soldes: Decimal


class ServiceAdministration:
    """Supervision des clients et des comptes."""

    def __init__(
        self,
        depot: Depot,
        session: Session,
        horloge: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._depot = depot
        self._session = session
        self._horloge = horloge

    def lister_clients(self) -> list[User]:
        """Renvoie tous les clients, sans les administrateurs."""
        self._session.exiger_admin()
        return [u for u in self._depot.lister_utilisateurs() if not u.admin]

    def rechercher_clients(
        self, nom: str = "", email: str = "", numero_compte: str = ""
    ) -> list[User]:
        """Clients qui répondent à tous les critères remplis (les vides sont ignorés).

        Le nom cherche dans le nom et le prénom, le numéro de compte dans l'IBAN
        (avec ou sans tirets) ; la casse ne compte pas.
        """
        clients = self.lister_clients()
        nom, email, numero = (
            nom.strip().lower(),
            email.strip().lower(),
            _compact(numero_compte),
        )
        ibans: dict[int, list[str]] = {}
        for compte in self._depot.lister_comptes():
            ibans.setdefault(compte.proprietaire_id, []).append(_compact(compte.iban))
        return [
            client
            for client in clients
            if (not nom or nom in f"{client.prenom} {client.nom}".lower())
            and (not email or email in client.email)
            and (not numero or any(numero in i for i in ibans.get(client.id, [])))
        ]

    def consulter_client(self, client_id: int) -> User:
        """Renvoie un client (pas un administrateur)."""
        self._session.exiger_admin()
        client = self._depot.trouver_utilisateur(client_id)
        if client is None or client.admin:
            raise ClientIntrouvableError("Ce client n'existe pas.")
        return client

    def comptes_du_client(self, client_id: int) -> list[CompteBancaire]:
        """Renvoie les comptes d'un client."""
        client = self.consulter_client(client_id)
        return self._depot.lister_comptes(client.id)

    def modifier_client(self, client_id: int, donnees: DonneesPersonnelles) -> User:
        """Modifie les informations d'un client, avec les mêmes règles que le profil."""
        client = self.consulter_client(client_id)
        email = exiger_email_disponible(self._depot, donnees.email, client.id)
        client.modifier_informations(
            nom=donnees.nom,
            prenom=donnees.prenom,
            email=email,
            telephone=donnees.telephone,
            adresse=donnees.adresse,
            date_naissance=lire_date(donnees.date_naissance),
        )
        self._depot.enregistrer_utilisateur(client)
        return client

    def supprimer_client(self, client_id: int) -> None:
        """Supprime un client et ses comptes, si tous ses comptes sont à 0,00 €.

        Comme pour RG6, l'argent ne doit pas disparaître avec le client.
        """
        client = self.consulter_client(client_id)
        for compte in self._depot.lister_comptes(client.id):
            if compte.solde != 0:
                raise SuppressionClientImpossibleError(
                    f"{client.nom_complet} a encore de l'argent sur le compte "
                    f"{compte.iban} : videz ses comptes avant de le supprimer."
                )
        self._depot.supprimer_utilisateur(client.id)

    def lister_comptes(self) -> list[CompteBancaire]:
        """Renvoie tous les comptes de la banque."""
        self._session.exiger_admin()
        return self._depot.lister_comptes()

    def noms_des_clients(self) -> dict[int, str]:
        """Associe l'identifiant de chaque utilisateur à son nom complet."""
        self._session.exiger_admin()
        return {u.id: u.nom_complet for u in self._depot.lister_utilisateurs()}

    def basculer_blocage(self, compte_id: int) -> CompteBancaire:
        """Bloque un compte actif, ou débloque un compte bloqué."""
        compte = self._compte(compte_id)
        if compte.est_bloque:
            compte.debloquer()
        else:
            compte.bloquer()
        self._depot.enregistrer_compte(compte)
        return compte

    def historique_compte(self, compte_id: int) -> list[Transaction]:
        """Transactions d'un compte, de la plus récente à la plus ancienne."""
        compte = self._compte(compte_id)
        transactions = self._depot.lister_transactions(
            FiltreHistorique(frozenset({compte.id}))
        )
        return sorted(transactions, key=lambda t: (t.date, t.id), reverse=True)

    def annuler_derniere_operation(self, compte_id: int) -> Transaction:
        """RG13 : annule la dernière opération du compte et historise l'annulation.

        Les soldes sont remis comme avant ; pour un virement, les deux comptes.
        Tout est vérifié avant de modifier quoi que ce soit (comme RG11).
        """
        compte = self._compte(compte_id)
        historique = self.historique_compte(compte.id)
        if not historique:
            raise AnnulationImpossibleError("Ce compte n'a aucune opération à annuler.")
        derniere = historique[0]
        if derniere.type is TypeTransaction.ANNULATION:
            raise AnnulationImpossibleError(
                "La dernière opération de ce compte est déjà une annulation."
            )

        mouvements = [(compte, not derniere.est_credit)]
        if derniere.type in _VIREMENTS:
            autre_id = (
                derniere.compte_destinataire_id
                if derniere.type is TypeTransaction.VIREMENT_EMIS
                else derniere.compte_source_id
            )
            autre = self._depot.trouver_compte(autre_id) if autre_id else None
            if autre is None:
                raise AnnulationImpossibleError(
                    "L'autre compte du virement n'existe plus : annulation impossible."
                )
            mouvements.append((autre, derniere.est_credit))

        montant = derniere.montant
        for concerne, credit in mouvements:
            if credit:
                concerne.verifier_credit(montant)
            else:
                concerne.verifier_debit(montant)
        annulations = []
        for concerne, credit in mouvements:
            if credit:
                concerne.crediter(montant)
            else:
                concerne.debiter(montant)
            annulations.append(
                Transaction(
                    id=self._depot.prochain_id_transaction(),
                    compte_source_id=None if credit else concerne.id,
                    compte_destinataire_id=concerne.id if credit else None,
                    type=TypeTransaction.ANNULATION,
                    montant=montant,
                    date=self._horloge(),
                    libelle=f"Annulation : {derniere.type.libelle.lower()} "
                    f"n°{derniere.id}",
                )
            )
        self._depot.enregistrer_operation([c for c, _ in mouvements], annulations)
        return annulations[0]

    def statistiques(self) -> Statistiques:
        """Nombre de clients et de comptes, somme des dépôts et des soldes."""
        clients = self.lister_clients()
        comptes = self._depot.lister_comptes()
        depots = self._depot.lister_transactions(
            FiltreHistorique(
                frozenset(c.id for c in comptes), type=TypeTransaction.DEPOT
            )
        )
        return Statistiques(
            nombre_clients=len(clients),
            nombre_comptes=len(comptes),
            total_depots=sum((t.montant for t in depots), Decimal("0.00")),
            total_soldes=sum((c.solde for c in comptes), Decimal("0.00")),
        )

    def _compte(self, compte_id: int) -> CompteBancaire:
        self._session.exiger_admin()
        compte = self._depot.trouver_compte(compte_id)
        if compte is None:
            raise CompteIntrouvableError("Ce compte n'existe pas.")
        return compte


def _compact(texte: str) -> str:
    return re.sub(r"[\s-]", "", texte).upper()
