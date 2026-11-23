"""Saisies de formulaire valides, pour les tests des services."""

from dataclasses import replace

from kampusbank.service.formulaires import DonneesPersonnelles

MOT_DE_PASSE_VALIDE = "Secret123"


def donnees_valides(**modifications: str) -> DonneesPersonnelles:
    """Renvoie un formulaire valide, avec éventuellement quelques champs changés."""
    base = DonneesPersonnelles(
        nom="Durand",
        prenom="Alice",
        email="alice@exemple.fr",
        telephone="0612345678",
        adresse="1 rue de Paris, 75001 Paris",
        date_naissance="15/04/2001",
    )
    return replace(base, **modifications)
