"""Validation centralisée des données saisies (EC5).

Chaque règle est écrite une seule fois ici et réutilisée par l'inscription, la
modification du profil et les opérations bancaires. Chaque fonction renvoie la
valeur nettoyée ou lève une exception métier.
"""

import re
from datetime import date, datetime
from decimal import Decimal

from kampusbank.domaine.exceptions import (
    ChampObligatoireError,
    DateInvalideError,
    EmailInvalideError,
    MontantInvalideError,
    MotDePasseInvalideError,
    TelephoneInvalideError,
)

_MOTIF_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
_MOTIF_TELEPHONE = re.compile(r"[0-9]{10}")
_MOTIF_MONTANT = re.compile(r"[0-9]{1,12}([.,][0-9]{1,2})?")
_LONGUEUR_MIN_MOT_DE_PASSE = 8
_OCTETS_MAX_MOT_DE_PASSE = 72
_FORMAT_DATE = "%d/%m/%Y"
_CENTIME = Decimal("0.01")


def valider_obligatoire(valeur: str, nom_du_champ: str) -> str:
    """Renvoie la valeur sans espaces superflus, ou lève une erreur si elle est vide."""
    valeur = valeur.strip()
    if not valeur:
        raise ChampObligatoireError(f"Le champ « {nom_du_champ} » est obligatoire.")
    return valeur


def normaliser_email(email: str) -> str:
    """Met l'email sous sa forme de référence : sans espaces, en minuscules."""
    return email.strip().lower()


def valider_email(email: str) -> str:
    """RG14 (format) : renvoie l'email normalisé s'il a un format valide."""
    email = normaliser_email(email)
    if not _MOTIF_EMAIL.fullmatch(email):
        raise EmailInvalideError(f"L'email « {email} » n'est pas valide.")
    return email


def valider_telephone(telephone: str) -> str:
    """RG15 : exactement 10 chiffres (les espaces saisis sont retirés)."""
    telephone = telephone.replace(" ", "")
    if not _MOTIF_TELEPHONE.fullmatch(telephone):
        raise TelephoneInvalideError(
            "Le téléphone doit compter exactement 10 chiffres."
        )
    return telephone


def valider_mot_de_passe(mot_de_passe: str) -> str:
    """RG16 : au moins 8 caractères, dont une majuscule et un chiffre.

    bcrypt ne prend en compte que les 72 premiers octets : au-delà, le mot de
    passe est refusé plutôt que tronqué en silence.
    """
    if len(mot_de_passe) < _LONGUEUR_MIN_MOT_DE_PASSE:
        raise MotDePasseInvalideError(
            f"Il faut au moins {_LONGUEUR_MIN_MOT_DE_PASSE} caractères au mot de passe."
        )
    if not any(caractere.isupper() for caractere in mot_de_passe):
        raise MotDePasseInvalideError("Le mot de passe doit contenir une majuscule.")
    if not any(caractere.isdigit() for caractere in mot_de_passe):
        raise MotDePasseInvalideError("Le mot de passe doit contenir un chiffre.")
    if len(mot_de_passe.encode("utf-8")) > _OCTETS_MAX_MOT_DE_PASSE:
        raise MotDePasseInvalideError("Le mot de passe est trop long.")
    return mot_de_passe


def lire_date(texte: str) -> date:
    """Convertit une date saisie au format JJ/MM/AAAA."""
    try:
        return datetime.strptime(texte.strip(), _FORMAT_DATE).date()
    except ValueError:
        raise DateInvalideError(
            f"La date « {texte} » doit être au format JJ/MM/AAAA."
        ) from None


def lire_date_facultative(texte: str) -> date | None:
    """Comme lire_date, mais un champ vide donne None (filtre sans borne)."""
    return lire_date(texte) if texte.strip() else None


def formater_date(valeur: date) -> str:
    """Écrit une date au format JJ/MM/AAAA, celui attendu par lire_date."""
    return valeur.strftime(_FORMAT_DATE)


def valider_montant(montant: Decimal) -> Decimal:
    """RG17 : montant strictement positif, avec 2 décimales au plus."""
    if not montant.is_finite() or montant <= 0:
        raise MontantInvalideError("Le montant doit être un nombre positif.")
    if montant != montant.quantize(_CENTIME):
        raise MontantInvalideError("Le montant ne peut pas avoir plus de 2 décimales.")
    return montant.quantize(_CENTIME)


def lire_montant(texte: str) -> Decimal:
    """RG17 : convertit un montant saisi (« 12 », « 12,5 », « 1 250.00 »).

    Le texte est converti directement en Decimal, sans passer par un float :
    en virgule flottante, 0.1 + 0.2 ne vaut pas 0.3.
    """
    compact = texte.replace(" ", "").replace(" ", "")
    if not _MOTIF_MONTANT.fullmatch(compact):
        raise MontantInvalideError(
            f"« {texte} » n'est pas un montant valide (exemple : 25,50)."
        )
    return valider_montant(Decimal(compact.replace(",", ".")))


def formater_montant(montant: Decimal) -> str:
    """Écrit un montant à la française : « 1 250,50 € »."""
    return f"{montant:,.2f} €".replace(",", " ").replace(".", ",")
