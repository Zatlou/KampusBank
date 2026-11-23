"""Consultation et modification du profil du client connecté."""

from kampusbank.domaine.user import User
from kampusbank.domaine.validation import lire_date
from kampusbank.persistance.depot import Depot
from kampusbank.service.formulaires import DonneesPersonnelles
from kampusbank.service.session import Session
from kampusbank.service.unicite import exiger_email_disponible


class ServiceProfil:
    """Fonctions client sur les informations personnelles (accès contrôlé, RG2)."""

    def __init__(self, depot: Depot, session: Session) -> None:
        self._depot = depot
        self._session = session

    def consulter(self) -> User:
        """Renvoie l'utilisateur connecté."""
        return self._session.exiger_connexion()

    def modifier(self, donnees: DonneesPersonnelles) -> User:
        """Valide et enregistre les nouvelles informations personnelles."""
        utilisateur = self._session.exiger_connexion()
        email = exiger_email_disponible(self._depot, donnees.email, utilisateur.id)
        utilisateur.modifier_informations(
            nom=donnees.nom,
            prenom=donnees.prenom,
            email=email,
            telephone=donnees.telephone,
            adresse=donnees.adresse,
            date_naissance=lire_date(donnees.date_naissance),
        )
        self._depot.enregistrer_utilisateur(utilisateur)
        return utilisateur
