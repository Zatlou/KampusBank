"""Contrôleur de l'espace administrateur (complété au jalon 3)."""

from kampusbank.domaine.exceptions import KampusBankError
from kampusbank.ihm.fenetre import FenetrePrincipale
from kampusbank.ihm.routeur import Ecran, Routeur
from kampusbank.ihm.vues.accueil_admin import VueAccueilAdmin
from kampusbank.service.administration import ServiceAdministration
from kampusbank.service.authentification import ServiceAuthentification
from kampusbank.service.formulaires import DonneesPersonnelles


class ControleurAdministration:
    """Écrans réservés aux administrateurs."""

    def __init__(
        self,
        fenetre: FenetrePrincipale,
        routeur: Routeur,
        service_administration: ServiceAdministration,
        service_authentification: ServiceAuthentification,
    ) -> None:
        self._fenetre = fenetre
        self._routeur = routeur
        self._administration = service_administration
        self._authentification = service_authentification

    def afficher_accueil(self) -> None:
        """Affiche la liste des clients."""
        try:
            clients = self._administration.lister_clients()
        except KampusBankError:
            self._routeur.aller_a(Ecran.CONNEXION)
            return
        vue = VueAccueilAdmin(
            self._fenetre.conteneur,
            clients=[DonneesPersonnelles.depuis_utilisateur(c) for c in clients],
            on_deconnexion=self._deconnecter,
        )
        self._fenetre.afficher(vue)

    def _deconnecter(self) -> None:
        self._authentification.deconnecter()
        self._routeur.aller_a(Ecran.CONNEXION)
