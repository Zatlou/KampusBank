"""Navigation entre les écrans."""

from collections.abc import Callable
from enum import Enum, auto


class Ecran(Enum):
    """Écrans de l'application."""

    CONNEXION = auto()
    INSCRIPTION = auto()
    TABLEAU_DE_BORD = auto()
    PROFIL = auto()
    ACCUEIL_ADMIN = auto()


class Routeur:
    """Associe chaque écran à la méthode qui l'affiche.

    Les contrôleurs naviguent par le routeur sans se connaître entre eux :
    c'est le module d'assemblage qui fait les associations.
    """

    def __init__(self) -> None:
        self._ecrans: dict[Ecran, Callable[[], object]] = {}

    def enregistrer(self, ecran: Ecran, afficher: Callable[[], object]) -> None:
        """Indique quelle méthode affiche cet écran."""
        self._ecrans[ecran] = afficher

    def aller_a(self, ecran: Ecran) -> None:
        """Affiche l'écran demandé."""
        self._ecrans[ecran]()
