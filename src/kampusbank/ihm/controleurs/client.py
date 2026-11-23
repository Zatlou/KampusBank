"""Contrôleur de l'espace client."""

from kampusbank.domaine.exceptions import KampusBankError, NonConnecteError
from kampusbank.ihm.fenetre import FenetrePrincipale
from kampusbank.ihm.routeur import Ecran, Routeur
from kampusbank.ihm.vues.profil import VueProfil
from kampusbank.ihm.vues.tableau_de_bord import VueTableauDeBord
from kampusbank.service.authentification import ServiceAuthentification
from kampusbank.service.formulaires import DonneesPersonnelles
from kampusbank.service.profil import ServiceProfil


class ControleurClient:
    """Tableau de bord, profil et déconnexion du client."""

    def __init__(
        self,
        fenetre: FenetrePrincipale,
        routeur: Routeur,
        service_profil: ServiceProfil,
        service_authentification: ServiceAuthentification,
    ) -> None:
        self._fenetre = fenetre
        self._routeur = routeur
        self._profil = service_profil
        self._authentification = service_authentification

    def afficher_tableau_de_bord(self) -> None:
        """Affiche les informations du client connecté."""
        try:
            utilisateur = self._profil.consulter()
        except NonConnecteError:
            self._routeur.aller_a(Ecran.CONNEXION)
            return
        vue = VueTableauDeBord(
            self._fenetre.conteneur,
            informations=DonneesPersonnelles.depuis_utilisateur(utilisateur),
            on_profil=lambda: self._routeur.aller_a(Ecran.PROFIL),
            on_deconnexion=self._deconnecter,
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
