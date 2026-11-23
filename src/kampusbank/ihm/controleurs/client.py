"""Contrôleur de l'espace client : tableau de bord, comptes et profil."""

from kampusbank.domaine.comptes import CompteBancaire
from kampusbank.domaine.exceptions import KampusBankError, NonConnecteError
from kampusbank.domaine.validation import formater_date, formater_montant
from kampusbank.ihm.fenetre import FenetrePrincipale
from kampusbank.ihm.routeur import Ecran, Routeur
from kampusbank.ihm.vues.detail_compte import VueDetailCompte
from kampusbank.ihm.vues.profil import VueProfil
from kampusbank.ihm.vues.tableau import LigneTableau
from kampusbank.ihm.vues.tableau_de_bord import VueTableauDeBord
from kampusbank.service.authentification import ServiceAuthentification
from kampusbank.service.comptes import ServiceComptes
from kampusbank.service.formulaires import DonneesPersonnelles
from kampusbank.service.profil import ServiceProfil


class ControleurClient:
    """Tableau de bord, ouverture, détail et suppression de comptes, profil."""

    def __init__(
        self,
        fenetre: FenetrePrincipale,
        routeur: Routeur,
        service_profil: ServiceProfil,
        service_comptes: ServiceComptes,
        service_authentification: ServiceAuthentification,
    ) -> None:
        self._fenetre = fenetre
        self._routeur = routeur
        self._profil = service_profil
        self._comptes = service_comptes
        self._authentification = service_authentification

    def afficher_tableau_de_bord(self) -> VueTableauDeBord | None:
        """Affiche les informations et les comptes du client connecté."""
        try:
            utilisateur = self._profil.consulter()
            comptes = self._comptes.lister()
        except NonConnecteError:
            self._routeur.aller_a(Ecran.CONNEXION)
            return None
        vue = VueTableauDeBord(
            self._fenetre.conteneur,
            informations=DonneesPersonnelles.depuis_utilisateur(utilisateur),
            comptes=[_ligne_compte(compte) for compte in comptes],
            types_de_compte=self._comptes.types_disponibles(),
            on_ouvrir_compte=lambda code: self._ouvrir_compte(vue, code),
            on_detail=self.afficher_detail,
            on_operations=lambda: self._routeur.aller_a(Ecran.OPERATIONS),
            on_historique=lambda: self._routeur.aller_a(Ecran.HISTORIQUE),
            on_profil=lambda: self._routeur.aller_a(Ecran.PROFIL),
            on_deconnexion=self._deconnecter,
        )
        self._fenetre.afficher(vue)
        return vue

    def afficher_detail(self, compte_id: int) -> None:
        """Affiche la fiche d'un compte du client."""
        try:
            compte = self._comptes.consulter(compte_id)
        except KampusBankError:
            self._routeur.aller_a(Ecran.TABLEAU_DE_BORD)
            return
        vue = VueDetailCompte(
            self._fenetre.conteneur,
            titre=compte.libelle,
            informations=[
                ("Type", compte.libelle),
                ("IBAN", compte.iban),
                ("Solde", formater_montant(compte.solde)),
                ("Statut", compte.statut.libelle),
                ("Ouvert le", formater_date(compte.date_creation.date())),
            ],
            on_supprimer=lambda: self._supprimer_compte(vue, compte_id),
            on_retour=lambda: self._routeur.aller_a(Ecran.TABLEAU_DE_BORD),
        )
        self._fenetre.afficher(vue)

    def afficher_profil(self) -> None:
        """Affiche le formulaire de modification du profil."""
        try:
            utilisateur = self._profil.consulter()
        except NonConnecteError:
            self._routeur.aller_a(Ecran.CONNEXION)
            return
        vue = VueProfil(
            self._fenetre.conteneur,
            informations=DonneesPersonnelles.depuis_utilisateur(utilisateur),
            on_enregistrer=lambda donnees: self._enregistrer_profil(vue, donnees),
            on_retour=lambda: self._routeur.aller_a(Ecran.TABLEAU_DE_BORD),
        )
        self._fenetre.afficher(vue)

    def _ouvrir_compte(self, vue: VueTableauDeBord, code: str) -> None:
        try:
            compte = self._comptes.ouvrir(code)
        except KampusBankError as erreur:
            vue.afficher_erreur(str(erreur))
            return
        nouvelle_vue = self.afficher_tableau_de_bord()
        if nouvelle_vue is not None:
            nouvelle_vue.afficher_succes(f"{compte.libelle} ouvert : {compte.iban}.")

    def _supprimer_compte(self, vue: VueDetailCompte, compte_id: int) -> None:
        try:
            self._comptes.supprimer(compte_id)
        except KampusBankError as erreur:
            vue.afficher_erreur(str(erreur))
            return
        nouvelle_vue = self.afficher_tableau_de_bord()
        if nouvelle_vue is not None:
            nouvelle_vue.afficher_succes("Le compte a été supprimé.")

    def _enregistrer_profil(self, vue: VueProfil, donnees: DonneesPersonnelles) -> None:
        try:
            self._profil.modifier(donnees)
        except KampusBankError as erreur:
            vue.afficher_erreur(str(erreur))
            return
        vue.afficher_succes("Vos informations sont enregistrées.")

    def _deconnecter(self) -> None:
        self._authentification.deconnecter()
        self._routeur.aller_a(Ecran.CONNEXION)


def _ligne_compte(compte: CompteBancaire) -> LigneTableau:
    return LigneTableau(
        compte.id,
        (
            compte.libelle,
            compte.iban,
            formater_montant(compte.solde),
            compte.statut.libelle,
        ),
    )
