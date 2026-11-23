"""Persistance dans un fichier JSON (implémentation par défaut)."""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

from kampusbank.domaine.user import User
from kampusbank.persistance.depot import Depot


class DepotJson(Depot):
    """Garde toutes les données dans un seul fichier JSON.

    Le fichier est lu une fois à la création, puis réécrit en entier à chaque
    enregistrement. L'écriture passe par un fichier temporaire renommé ensuite :
    si l'application s'arrête au milieu, l'ancien fichier reste intact.
    """

    def __init__(self, fichier: Path) -> None:
        self._fichier = fichier
        self._donnees = self._charger()

    def prochain_id_utilisateur(self) -> int:
        """Réserve et renvoie un identifiant jamais attribué."""
        self._donnees["compteurs"]["utilisateurs"] += 1
        self._sauvegarder()
        identifiant: int = self._donnees["compteurs"]["utilisateurs"]
        return identifiant

    def enregistrer_utilisateur(self, utilisateur: User) -> None:
        """Ajoute l'utilisateur, ou le remplace s'il existe déjà (même id)."""
        lignes: list[dict[str, Any]] = self._donnees["utilisateurs"]
        nouvelle_ligne = _utilisateur_vers_dict(utilisateur)
        for position, ligne in enumerate(lignes):
            if ligne["id"] == utilisateur.id:
                lignes[position] = nouvelle_ligne
                break
        else:
            lignes.append(nouvelle_ligne)
        self._sauvegarder()

    def trouver_utilisateur_par_email(self, email: str) -> User | None:
        """Renvoie l'utilisateur qui a cet email (déjà normalisé), ou None."""
        for ligne in self._donnees["utilisateurs"]:
            if ligne["email"] == email:
                return _dict_vers_utilisateur(ligne)
        return None

    def lister_utilisateurs(self) -> list[User]:
        """Renvoie tous les utilisateurs, administrateurs compris."""
        return [
            _dict_vers_utilisateur(ligne) for ligne in self._donnees["utilisateurs"]
        ]

    def _charger(self) -> dict[str, Any]:
        if not self._fichier.exists():
            return {"compteurs": {"utilisateurs": 0}, "utilisateurs": []}
        with self._fichier.open(encoding="utf-8") as fichier:
            donnees: dict[str, Any] = json.load(fichier)
        return donnees

    def _sauvegarder(self) -> None:
        self._fichier.parent.mkdir(parents=True, exist_ok=True)
        temporaire = self._fichier.with_name(self._fichier.name + ".tmp")
        with temporaire.open("w", encoding="utf-8") as fichier:
            json.dump(self._donnees, fichier, ensure_ascii=False, indent=2)
        temporaire.replace(self._fichier)


def _utilisateur_vers_dict(utilisateur: User) -> dict[str, Any]:
    bloque_jusqu_a = utilisateur.bloque_jusqu_a
    return {
        "id": utilisateur.id,
        "nom": utilisateur.nom,
        "prenom": utilisateur.prenom,
        "email": utilisateur.email,
        "telephone": utilisateur.telephone,
        "adresse": utilisateur.adresse,
        "date_naissance": utilisateur.date_naissance.isoformat(),
        "mot_de_passe_hash": utilisateur.mot_de_passe_hash,
        "admin": utilisateur.admin,
        "echecs_connexion": utilisateur.echecs_connexion,
        "bloque_jusqu_a": bloque_jusqu_a.isoformat() if bloque_jusqu_a else None,
    }


def _dict_vers_utilisateur(ligne: dict[str, Any]) -> User:
    bloque_jusqu_a = ligne["bloque_jusqu_a"]
    return User(
        id=ligne["id"],
        nom=ligne["nom"],
        prenom=ligne["prenom"],
        email=ligne["email"],
        telephone=ligne["telephone"],
        adresse=ligne["adresse"],
        date_naissance=date.fromisoformat(ligne["date_naissance"]),
        mot_de_passe_hash=ligne["mot_de_passe_hash"],
        admin=ligne["admin"],
        echecs_connexion=ligne["echecs_connexion"],
        bloque_jusqu_a=datetime.fromisoformat(bloque_jusqu_a)
        if bloque_jusqu_a
        else None,
    )
