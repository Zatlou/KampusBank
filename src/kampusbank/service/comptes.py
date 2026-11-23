"""Gestion des comptes du client connecté : liste, détail, ouverture, suppression."""

from collections.abc import Callable
from datetime import datetime

from kampusbank.domaine.comptes import CompteBancaire, classe_de_compte, types_de_compte
from kampusbank.persistance.depot import Depot
from kampusbank.service.proprietaire import compte_du_client
from kampusbank.service.session import Session


class ServiceComptes:
    """Comptes bancaires du client connecté (RG4 à RG6)."""

    def __init__(
        self,
        depot: Depot,
        session: Session,
        generer_iban: Callable[[], str],
        horloge: Callable[[], datetime],
    ) -> None:
        self._depot = depot
        self._session = session
        self._generer_iban = generer_iban
        self._horloge = horloge

    def types_disponibles(self) -> list[tuple[str, str]]:
        """Renvoie (code, libellé) de chaque type de compte qu'on peut ouvrir."""
        return [(classe.CODE, classe.LIBELLE) for classe in types_de_compte()]

    def lister(self) -> list[CompteBancaire]:
        """Renvoie les comptes du client connecté (RG5 : il peut en avoir plusieurs)."""
        client = self._session.exiger_connexion()
        return self._depot.lister_comptes(client.id)

    def consulter(self, compte_id: int) -> CompteBancaire:
        """Renvoie un compte du client connecté."""
        client = self._session.exiger_connexion()
        return compte_du_client(self._depot, client, compte_id)

    def ouvrir(self, code_type: str) -> CompteBancaire:
        """Ouvre un compte du type demandé, à 0,00 €, avec un IBAN unique (RG4)."""
        client = self._session.exiger_connexion()
        classe = classe_de_compte(code_type)
        compte = classe(
            id=self._depot.prochain_id_compte(),
            proprietaire_id=client.id,
            iban=self._iban_inutilise(),
            date_creation=self._horloge(),
        )
        self._depot.enregistrer_compte(compte)
        return compte

    def supprimer(self, compte_id: int) -> None:
        """Supprime un compte du client, seulement si son solde vaut 0,00 € (RG6)."""
        compte = self.consulter(compte_id)
        compte.verifier_suppression()
        self._depot.supprimer_compte(compte.id)

    def _iban_inutilise(self) -> str:
        iban = self._generer_iban()
        while self._depot.trouver_compte_par_iban(iban) is not None:
            iban = self._generer_iban()
        return iban
