"""Inscription, connexion et déconnexion (RG1, RG3, RG14 à RG16)."""

from collections.abc import Callable
from datetime import datetime, timedelta

from kampusbank.domaine.exceptions import (
    IdentifiantsInvalidesError,
    UtilisateurBloqueError,
)
from kampusbank.domaine.user import User
from kampusbank.domaine.validation import (
    lire_date,
    normaliser_email,
    valider_mot_de_passe,
)
from kampusbank.persistance.depot import Depot
from kampusbank.service.formulaires import DonneesPersonnelles
from kampusbank.service.hachage import HacheurMotDePasse
from kampusbank.service.session import Session
from kampusbank.service.unicite import exiger_email_disponible

_MESSAGE_IDENTIFIANTS = "Email ou mot de passe incorrect."


class ServiceAuthentification:
    """Crée les comptes utilisateurs et ouvre ou ferme la session."""

    def __init__(
        self,
        depot: Depot,
        hacheur: HacheurMotDePasse,
        session: Session,
        echecs_max: int,
        duree_blocage: timedelta,
        horloge: Callable[[], datetime],
    ) -> None:
        self._depot = depot
        self._hacheur = hacheur
        self._session = session
        self._echecs_max = echecs_max
        self._duree_blocage = duree_blocage
        self._horloge = horloge

    def inscrire(self, donnees: DonneesPersonnelles, mot_de_passe: str) -> User:
        """Crée un compte client ; le mot de passe est haché avant l'enregistrement."""
        return self._creer_utilisateur(donnees, mot_de_passe, admin=False)

    def creer_administrateur_initial(
        self, donnees: DonneesPersonnelles, mot_de_passe: str
    ) -> None:
        """Crée l'administrateur de la configuration s'il n'existe pas encore."""
        email = normaliser_email(donnees.email)
        if self._depot.trouver_utilisateur_par_email(email) is None:
            self._creer_utilisateur(donnees, mot_de_passe, admin=True)

    def connecter(self, email: str, mot_de_passe: str) -> User:
        """Vérifie les identifiants et ouvre la session (RG3 : blocage après échecs)."""
        maintenant = self._horloge()
        utilisateur = self._depot.trouver_utilisateur_par_email(normaliser_email(email))
        if utilisateur is None:
            raise IdentifiantsInvalidesError(_MESSAGE_IDENTIFIANTS)
        self._refuser_si_bloque(utilisateur, maintenant)

        if not self._hacheur.verifier(mot_de_passe, utilisateur.mot_de_passe_hash):
            utilisateur.enregistrer_echec_connexion(
                maintenant, self._echecs_max, self._duree_blocage
            )
            self._depot.enregistrer_utilisateur(utilisateur)
            self._refuser_si_bloque(utilisateur, maintenant)
            raise IdentifiantsInvalidesError(_MESSAGE_IDENTIFIANTS)

        utilisateur.reinitialiser_echecs_connexion()
        self._depot.enregistrer_utilisateur(utilisateur)
        self._session.ouvrir(utilisateur)
        return utilisateur

    def deconnecter(self) -> None:
        """Ferme la session en cours."""
        self._session.fermer()

    def _creer_utilisateur(
        self, donnees: DonneesPersonnelles, mot_de_passe: str, admin: bool
    ) -> User:
        valider_mot_de_passe(mot_de_passe)
        email = exiger_email_disponible(self._depot, donnees.email)
        date_naissance = lire_date(donnees.date_naissance)
        utilisateur = User(
            id=self._depot.prochain_id_utilisateur(),
            nom=donnees.nom,
            prenom=donnees.prenom,
            email=email,
            telephone=donnees.telephone,
            adresse=donnees.adresse,
            date_naissance=date_naissance,
            mot_de_passe_hash=self._hacheur.hacher(mot_de_passe),
            admin=admin,
        )
        self._depot.enregistrer_utilisateur(utilisateur)
        return utilisateur

    def _refuser_si_bloque(self, utilisateur: User, maintenant: datetime) -> None:
        fin = utilisateur.fin_de_blocage(maintenant)
        if fin is not None:
            raise UtilisateurBloqueError(
                f"Trop d'échecs de connexion : compte bloqué jusqu'à {fin:%H:%M}."
            )
