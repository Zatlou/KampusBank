"""Données échangées entre l'interface et les services."""

from dataclasses import dataclass

from kampusbank.domaine.user import User
from kampusbank.domaine.validation import formater_date


@dataclass(frozen=True)
class DonneesPersonnelles:
    """Informations personnelles telles qu'elles sont saisies dans un formulaire.

    Tout est en texte : la conversion et la validation sont faites par les
    services, jamais par l'interface.
    """

    nom: str
    prenom: str
    email: str
    telephone: str
    adresse: str
    date_naissance: str

    @classmethod
    def depuis_utilisateur(cls, utilisateur: User) -> "DonneesPersonnelles":
        """Prépare les informations d'un utilisateur pour les afficher."""
        return cls(
            nom=utilisateur.nom,
            prenom=utilisateur.prenom,
            email=utilisateur.email,
            telephone=utilisateur.telephone,
            adresse=utilisateur.adresse,
            date_naissance=formater_date(utilisateur.date_naissance),
        )
