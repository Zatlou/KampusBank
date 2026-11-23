"""Objets du domaine réutilisés par plusieurs fichiers de tests."""

from datetime import date, datetime, timedelta

from kampusbank.domaine.user import User

ECHECS_MAX = 5
DUREE_BLOCAGE_MINUTES = 15


class HorlogeFactice:
    """Horloge que les tests font avancer à la main (RG3 sans attendre 15 min)."""

    def __init__(self) -> None:
        self.maintenant = datetime(2026, 11, 23, 10, 0)

    def __call__(self) -> datetime:
        return self.maintenant

    def avancer(self, minutes: int) -> None:
        self.maintenant += timedelta(minutes=minutes)


def utilisateur_valide(
    email: str = "alice@exemple.fr", telephone: str = "0612345678"
) -> User:
    """Construit directement un User valide (sans passer par les services)."""
    return User(
        id=1,
        nom="Durand",
        prenom="Alice",
        email=email,
        telephone=telephone,
        adresse="1 rue de Paris, 75001 Paris",
        date_naissance=date(2001, 4, 15),
        mot_de_passe_hash="empreinte",
    )
