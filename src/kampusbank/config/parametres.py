"""Chargement des paramètres de l'application depuis kampusbank.toml."""

import tomllib
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


@dataclass(frozen=True)
class ParametresMySQL:
    """Connexion à la base MySQL (persistance facultative)."""

    hote: str
    port: int
    utilisateur: str
    mot_de_passe: str
    base: str


@dataclass(frozen=True)
class ParametresPersistance:
    """Type de persistance choisi, fichier JSON et, en option, base MySQL."""

    type: str
    fichier: Path
    mysql: ParametresMySQL | None = None


@dataclass(frozen=True)
class ParametresAdministrateur:
    """Administrateur initial, créé au premier lancement."""

    email: str
    mot_de_passe: str
    nom: str
    prenom: str
    telephone: str
    adresse: str
    date_naissance: str


@dataclass(frozen=True)
class ParametresSecurite:
    """Seuils de la règle RG3 et coût du hachage des mots de passe."""

    echecs_max: int
    duree_blocage_minutes: int
    cout_bcrypt: int


@dataclass(frozen=True)
class ParametresOperations:
    """Limites des opérations bancaires (RG8 à RG10)."""

    montant_minimum: Decimal
    retrait_maximum: Decimal


@dataclass(frozen=True)
class Parametres:
    """Ensemble des paramètres lus dans le fichier de configuration."""

    persistance: ParametresPersistance
    administrateur: ParametresAdministrateur
    securite: ParametresSecurite
    operations: ParametresOperations


def charger_parametres(chemin: Path) -> Parametres:
    """Lit le fichier TOML indiqué et renvoie des paramètres typés.

    Le fichier de données est résolu par rapport au dossier du fichier de
    configuration : l'application trouve ses données quel que soit le dossier
    depuis lequel on la lance.
    """
    with chemin.open("rb") as fichier:
        brut = tomllib.load(fichier)

    persistance = brut["persistance"]
    administrateur = brut["administrateur"]
    securite = brut["securite"]
    operations = brut["operations"]

    return Parametres(
        persistance=ParametresPersistance(
            type=str(persistance["type"]),
            fichier=chemin.parent / str(persistance["fichier"]),
            mysql=_lire_mysql(persistance.get("mysql")),
        ),
        administrateur=ParametresAdministrateur(
            email=str(administrateur["email"]),
            mot_de_passe=str(administrateur["mot_de_passe"]),
            nom=str(administrateur["nom"]),
            prenom=str(administrateur["prenom"]),
            telephone=str(administrateur["telephone"]),
            adresse=str(administrateur["adresse"]),
            date_naissance=str(administrateur["date_naissance"]),
        ),
        securite=ParametresSecurite(
            echecs_max=int(securite["echecs_max"]),
            duree_blocage_minutes=int(securite["duree_blocage_minutes"]),
            cout_bcrypt=int(securite["cout_bcrypt"]),
        ),
        operations=ParametresOperations(
            montant_minimum=Decimal(str(operations["montant_minimum"])),
            retrait_maximum=Decimal(str(operations["retrait_maximum"])),
        ),
    )


def _lire_mysql(section: dict[str, object] | None) -> ParametresMySQL | None:
    if section is None:
        return None
    return ParametresMySQL(
        hote=str(section["hote"]),
        port=int(str(section["port"])),
        utilisateur=str(section["utilisateur"]),
        mot_de_passe=str(section["mot_de_passe"]),
        base=str(section["base"]),
    )
