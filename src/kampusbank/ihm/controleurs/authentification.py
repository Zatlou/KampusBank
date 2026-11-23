"""Contrôleur des écrans de connexion et d'inscription."""

from kampusbank.domaine.exceptions import KampusBankError
from kampusbank.ihm.fenetre import FenetrePrincipale
from kampusbank.ihm.routeur import Ecran, Routeur
from kampusbank.ihm.vues.connexion import VueConnexion
from kampusbank.ihm.vues.inscription import VueInscription
from kampusbank.service.authentification import ServiceAuthentification
from kampusbank.service.formulaires import DonneesPersonnelles


class ControleurAuthentification:
    """Transmet les saisies au service d'authentification et affiche le résultat."""

    def __init__(
        self,
        fenetre: FenetrePrincipale,
        routeur: Routeur,
        service: ServiceAuthentification,
    ) -> None:
        self._fenetre = fenetre
        self._routeur = routeur
        self._service = service

    def afficher_connexion(self) -> VueConnexion:
        """Affiche l'écran de connexion et le renvoie."""
        vue = VueConnexion(
            self._fenetre.conteneur,
            on_connexion=lambda email, mot_de_passe: self._connecter(
                vue, email, mot_de_passe
            ),
            on_inscription=lambda: self._routeur.aller_a(Ecran.INSCRIPTION),
        )
        self._fenetre.afficher(vue)
        return vue

    def afficher_inscription(self) -> None:
        """Affiche le formulaire d'inscription."""
        vue = VueInscription(
            self._fenetre.conteneur,
            on_inscription=lambda donnees, mot_de_passe: self._inscrire(
                vue, donnees, mot_de_passe
            ),
            on_retour=lambda: self._routeur.aller_a(Ecran.CONNEXION),
        )
        self._fenetre.afficher(vue)

    def _connecter(self, vue: VueConnexion, email: str, mot_de_passe: str) -> None:
        try:
            utilisateur = self._service.connecter(email, mot_de_passe)
        except KampusBankError as erreur:
            vue.afficher_erreur(str(erreur))
            return
        if utilisateur.admin:
            self._routeur.aller_a(Ecran.ACCUEIL_ADMIN)
        else:
            self._routeur.aller_a(Ecran.TABLEAU_DE_BORD)

    def _inscrire(
        self, vue: VueInscription, donnees: DonneesPersonnelles, mot_de_passe: str
    ) -> None:
        try:
            self._service.inscrire(donnees, mot_de_passe)
        except KampusBankError as erreur:
            vue.afficher_erreur(str(erreur))
            return
        self.afficher_connexion().afficher_succes(
            "Votre compte est créé : vous pouvez vous connecter."
        )
