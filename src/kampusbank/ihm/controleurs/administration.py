"""Contrôleur de l'espace administrateur."""

from collections.abc import Callable

from kampusbank.domaine.comptes import CompteBancaire
from kampusbank.domaine.exceptions import KampusBankError
from kampusbank.domaine.transaction import Transaction
from kampusbank.domaine.user import User
from kampusbank.domaine.validation import formater_montant
from kampusbank.ihm.fenetre import FenetrePrincipale
from kampusbank.ihm.routeur import Ecran, Routeur
from kampusbank.ihm.vues.accueil_admin import VueAccueilAdmin
from kampusbank.ihm.vues.base import Vue
from kampusbank.ihm.vues.comptes_admin import VueComptesAdmin
from kampusbank.ihm.vues.fiche_client import VueFicheClient
from kampusbank.ihm.vues.historique_compte import VueHistoriqueCompte
from kampusbank.ihm.vues.tableau import LigneTableau
from kampusbank.service.administration import ServiceAdministration
from kampusbank.service.authentification import ServiceAuthentification
from kampusbank.service.formulaires import DonneesPersonnelles

Affichage = Callable[[], Vue | None]


class ControleurAdministration:
    """Clients, comptes, blocage, annulation (RG13) et statistiques."""

    def __init__(
        self,
        fenetre: FenetrePrincipale,
        routeur: Routeur,
        service_administration: ServiceAdministration,
        service_authentification: ServiceAuthentification,
    ) -> None:
        self._fenetre = fenetre
        self._routeur = routeur
        self._admin = service_administration
        self._authentification = service_authentification

    def afficher_accueil(self) -> Vue | None:
        """Statistiques, recherche et liste des clients."""
        try:
            stats = self._admin.statistiques()
            clients = self._lignes_clients(self._admin.lister_clients())
        except KampusBankError:
            self._routeur.aller_a(Ecran.CONNEXION)
            return None
        vue = VueAccueilAdmin(
            self._fenetre.conteneur,
            statistiques=[
                ("clients", str(stats.nombre_clients)),
                ("comptes", str(stats.nombre_comptes)),
                ("somme des dépôts", formater_montant(stats.total_depots)),
                ("total des soldes", formater_montant(stats.total_soldes)),
            ],
            clients=clients,
            on_rechercher=lambda nom, email, compte: self._rechercher(
                vue, nom, email, compte
            ),
            on_client=self.afficher_client,
            on_comptes=self.afficher_comptes,
            on_deconnexion=self._deconnecter,
        )
        self._fenetre.afficher(vue)
        return vue

    def afficher_client(self, client_id: int) -> Vue | None:
        """Fiche d'un client et de ses comptes."""
        try:
            client = self._admin.consulter_client(client_id)
            comptes = self._lignes_comptes(self._admin.comptes_du_client(client_id))
        except KampusBankError:
            return self.afficher_accueil()
        retour: Affichage = lambda: self.afficher_client(client_id)  # noqa: E731
        vue = VueFicheClient(
            self._fenetre.conteneur,
            titre=client.nom_complet,
            informations=DonneesPersonnelles.depuis_utilisateur(client),
            comptes=comptes,
            on_enregistrer=lambda donnees: self._modifier_client(
                vue, client_id, donnees
            ),
            on_supprimer=lambda: self._supprimer_client(vue, client_id),
            on_bloquer=lambda compte: self._agir(
                vue, lambda: self._message_blocage(compte), retour
            ),
            on_historique=lambda compte: self.afficher_historique(compte, retour),
            on_annuler=lambda compte: self._agir(
                vue, lambda: self._message_annulation(compte), retour
            ),
            on_retour=self.afficher_accueil,
        )
        self._fenetre.afficher(vue)
        return vue

    def afficher_comptes(self) -> Vue | None:
        """Tous les comptes de la banque."""
        try:
            comptes = self._lignes_comptes(self._admin.lister_comptes())
        except KampusBankError:
            self._routeur.aller_a(Ecran.CONNEXION)
            return None
        vue = VueComptesAdmin(
            self._fenetre.conteneur,
            comptes=comptes,
            on_bloquer=lambda compte: self._agir(
                vue, lambda: self._message_blocage(compte), self.afficher_comptes
            ),
            on_historique=lambda compte: self.afficher_historique(
                compte, self.afficher_comptes
            ),
            on_annuler=lambda compte: self._agir(
                vue, lambda: self._message_annulation(compte), self.afficher_comptes
            ),
            on_retour=self.afficher_accueil,
        )
        self._fenetre.afficher(vue)
        return vue

    def afficher_historique(self, compte_id: int, retour: Affichage) -> None:
        """Historique d'un compte."""
        try:
            transactions = self._admin.historique_compte(compte_id)
            iban = next(
                c.iban for c in self._admin.lister_comptes() if c.id == compte_id
            )
        except KampusBankError:
            return
        vue = VueHistoriqueCompte(
            self._fenetre.conteneur,
            titre=f"Historique — {iban}",
            lignes=[_ligne_transaction(t) for t in transactions],
            on_retour=retour,
        )
        self._fenetre.afficher(vue)

    def _rechercher(
        self, vue: VueAccueilAdmin, nom: str, email: str, compte: str
    ) -> None:
        try:
            clients = self._admin.rechercher_clients(nom, email, compte)
        except KampusBankError as erreur:
            vue.afficher_erreur(str(erreur))
            return
        vue.afficher_clients(self._lignes_clients(clients))

    def _modifier_client(
        self, vue: Vue, client_id: int, donnees: DonneesPersonnelles
    ) -> None:
        try:
            self._admin.modifier_client(client_id, donnees)
        except KampusBankError as erreur:
            vue.afficher_erreur(str(erreur))
            return
        vue.afficher_succes("Informations du client enregistrées.")

    def _supprimer_client(self, vue: Vue, client_id: int) -> None:
        try:
            self._admin.supprimer_client(client_id)
        except KampusBankError as erreur:
            vue.afficher_erreur(str(erreur))
            return
        accueil = self.afficher_accueil()
        if accueil is not None:
            accueil.afficher_succes("Le client a été supprimé.")

    def _agir(self, vue: Vue, action: Callable[[], str], rafraichir: Affichage) -> None:
        try:
            message = action()
        except KampusBankError as erreur:
            vue.afficher_erreur(str(erreur))
            return
        nouvelle_vue = rafraichir()
        if nouvelle_vue is not None:
            nouvelle_vue.afficher_succes(message)

    def _message_blocage(self, compte_id: int) -> str:
        compte = self._admin.basculer_blocage(compte_id)
        return f"Compte {compte.iban} : {compte.statut.libelle.lower()}."

    def _message_annulation(self, compte_id: int) -> str:
        annulation = self._admin.annuler_derniere_operation(compte_id)
        return f"{annulation.libelle} effectuée, soldes restaurés."

    def _lignes_clients(self, clients: list[User]) -> list[LigneTableau]:
        nombre: dict[int, int] = {}
        for compte in self._admin.lister_comptes():
            nombre[compte.proprietaire_id] = nombre.get(compte.proprietaire_id, 0) + 1
        return [
            LigneTableau(
                c.id,
                (c.nom, c.prenom, c.email, c.telephone, str(nombre.get(c.id, 0))),
            )
            for c in clients
        ]

    def _lignes_comptes(self, comptes: list[CompteBancaire]) -> list[LigneTableau]:
        noms = self._admin.noms_des_clients()
        return [
            LigneTableau(
                c.id,
                (
                    noms.get(c.proprietaire_id, "?"),
                    c.libelle,
                    c.iban,
                    formater_montant(c.solde),
                    c.statut.libelle,
                ),
                "alerte" if c.est_bloque else "",
            )
            for c in comptes
        ]

    def _deconnecter(self) -> None:
        self._authentification.deconnecter()
        self._routeur.aller_a(Ecran.CONNEXION)


def _ligne_transaction(transaction: Transaction) -> LigneTableau:
    signe = "+" if transaction.est_credit else "−"
    return LigneTableau(
        transaction.id,
        (
            f"{transaction.date:%d/%m/%Y %H:%M}",
            transaction.type.libelle,
            transaction.libelle,
            f"{signe} {formater_montant(transaction.montant)}",
        ),
        "credit" if transaction.est_credit else "debit",
    )
