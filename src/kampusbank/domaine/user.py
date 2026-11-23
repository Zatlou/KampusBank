"""Utilisateur de KampusBank : client ou administrateur."""

from datetime import date, datetime, timedelta

from kampusbank.domaine.validation import (
    valider_email,
    valider_obligatoire,
    valider_telephone,
)


class User:
    """Utilisateur de l'application.

    Les attributs sont privés (préfixe _) et exposés en lecture par des
    propriétés : on ne les modifie que par des méthodes qui valident les
    données, si bien qu'un User est toujours dans un état valide.
    """

    _nom: str
    _prenom: str
    _email: str
    _telephone: str
    _adresse: str
    _date_naissance: date

    def __init__(
        self,
        *,
        id: int,
        nom: str,
        prenom: str,
        email: str,
        telephone: str,
        adresse: str,
        date_naissance: date,
        mot_de_passe_hash: str,
        admin: bool = False,
        echecs_connexion: int = 0,
        bloque_jusqu_a: datetime | None = None,
    ) -> None:
        self._id = id
        self._mot_de_passe_hash = mot_de_passe_hash
        self._admin = admin
        self._echecs_connexion = echecs_connexion
        self._bloque_jusqu_a = bloque_jusqu_a
        self.modifier_informations(
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone,
            adresse=adresse,
            date_naissance=date_naissance,
        )

    @property
    def id(self) -> int:
        """Identifiant unique."""
        return self._id

    @property
    def nom(self) -> str:
        """Nom de famille."""
        return self._nom

    @property
    def prenom(self) -> str:
        """Prénom."""
        return self._prenom

    @property
    def nom_complet(self) -> str:
        """Prénom et nom, pour l'affichage."""
        return f"{self._prenom} {self._nom}"

    @property
    def email(self) -> str:
        """Email, unique et normalisé en minuscules."""
        return self._email

    @property
    def telephone(self) -> str:
        """Téléphone à 10 chiffres."""
        return self._telephone

    @property
    def adresse(self) -> str:
        """Adresse postale."""
        return self._adresse

    @property
    def date_naissance(self) -> date:
        """Date de naissance."""
        return self._date_naissance

    @property
    def mot_de_passe_hash(self) -> str:
        """Empreinte bcrypt du mot de passe (jamais le mot de passe en clair)."""
        return self._mot_de_passe_hash

    @property
    def admin(self) -> bool:
        """Vrai si l'utilisateur est administrateur."""
        return self._admin

    @property
    def echecs_connexion(self) -> int:
        """Nombre d'échecs de connexion consécutifs (RG3)."""
        return self._echecs_connexion

    @property
    def bloque_jusqu_a(self) -> datetime | None:
        """Fin du blocage en cours ou passé (RG3), None si jamais bloqué depuis."""
        return self._bloque_jusqu_a

    def modifier_informations(
        self,
        *,
        nom: str,
        prenom: str,
        email: str,
        telephone: str,
        adresse: str,
        date_naissance: date,
    ) -> None:
        """Remplace les informations personnelles après les avoir toutes validées.

        Tout est validé avant la moindre affectation : si une donnée est
        invalide, l'utilisateur reste exactement dans son état précédent.
        """
        nom = valider_obligatoire(nom, "nom")
        prenom = valider_obligatoire(prenom, "prénom")
        email = valider_email(email)
        telephone = valider_telephone(telephone)

        self._nom = nom
        self._prenom = prenom
        self._email = email
        self._telephone = telephone
        self._adresse = adresse.strip()
        self._date_naissance = date_naissance

    def fin_de_blocage(self, maintenant: datetime) -> datetime | None:
        """Renvoie l'heure de fin du blocage s'il est encore actif, sinon None (RG3)."""
        if self._bloque_jusqu_a is not None and maintenant < self._bloque_jusqu_a:
            return self._bloque_jusqu_a
        return None

    def enregistrer_echec_connexion(
        self, maintenant: datetime, echecs_max: int, duree_blocage: timedelta
    ) -> None:
        """Compte un échec et bloque l'utilisateur au seuil atteint (RG3).

        Si un blocage précédent est terminé, le compteur repart de zéro.
        """
        if self._bloque_jusqu_a is not None and maintenant >= self._bloque_jusqu_a:
            self.reinitialiser_echecs_connexion()
        self._echecs_connexion += 1
        if self._echecs_connexion >= echecs_max:
            self._bloque_jusqu_a = maintenant + duree_blocage

    def reinitialiser_echecs_connexion(self) -> None:
        """Remet le compteur d'échecs à zéro et lève le blocage (connexion réussie)."""
        self._echecs_connexion = 0
        self._bloque_jusqu_a = None
