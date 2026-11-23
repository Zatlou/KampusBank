"""Persistance dans un fichier JSON (implémentation par défaut)."""

import copy
import json
from collections.abc import Callable
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from kampusbank.domaine.comptes import CompteBancaire, StatutCompte, classe_de_compte
from kampusbank.domaine.historique import FiltreHistorique
from kampusbank.domaine.transaction import Transaction, TypeTransaction
from kampusbank.domaine.user import User
from kampusbank.persistance.depot import Depot

_TABLES = ("utilisateurs", "comptes", "transactions")

Ligne = dict[str, Any]


class DepotJson(Depot):
    """Garde toutes les données dans un seul fichier JSON.

    Chaque modification est appliquée à une copie des données, écrite dans un
    fichier temporaire, puis le fichier temporaire remplace l'ancien. Si quoi
    que ce soit échoue en route, ni le fichier ni la mémoire ne sont modifiés :
    c'est ce qui rend un virement atomique (RG11).
    Les montants sont écrits en texte (« 12.50 ») et jamais en nombre à virgule
    flottante, pour rester exacts.
    """

    def __init__(self, fichier: Path) -> None:
        self._fichier = fichier
        self._donnees = self._charger()

    def prochain_id_utilisateur(self) -> int:
        """Réserve et renvoie un identifiant d'utilisateur jamais attribué."""
        return self._prochain_id("utilisateurs")

    def enregistrer_utilisateur(self, utilisateur: User) -> None:
        """Ajoute l'utilisateur, ou le remplace s'il existe déjà (même id)."""
        ligne = _utilisateur_vers_dict(utilisateur)
        self._modifier(lambda donnees: _remplacer(donnees["utilisateurs"], ligne))

    def trouver_utilisateur_par_email(self, email: str) -> User | None:
        """Renvoie l'utilisateur qui a cet email (déjà normalisé), ou None."""
        ligne = self._trouver("utilisateurs", "email", email)
        return _dict_vers_utilisateur(ligne) if ligne else None

    def lister_utilisateurs(self) -> list[User]:
        """Renvoie tous les utilisateurs, administrateurs compris."""
        return [
            _dict_vers_utilisateur(ligne) for ligne in self._donnees["utilisateurs"]
        ]

    def trouver_utilisateur(self, utilisateur_id: int) -> User | None:
        """Renvoie l'utilisateur qui a cet identifiant, ou None."""
        ligne = self._trouver("utilisateurs", "id", utilisateur_id)
        return _dict_vers_utilisateur(ligne) if ligne else None

    def supprimer_utilisateur(self, utilisateur_id: int) -> None:
        """Supprime l'utilisateur et ses comptes ; l'historique est conservé."""

        def retirer(donnees: Ligne) -> None:
            donnees["utilisateurs"] = [
                u for u in donnees["utilisateurs"] if u["id"] != utilisateur_id
            ]
            donnees["comptes"] = [
                c for c in donnees["comptes"] if c["proprietaire_id"] != utilisateur_id
            ]

        self._modifier(retirer)

    def prochain_id_compte(self) -> int:
        """Réserve et renvoie un identifiant de compte jamais attribué."""
        return self._prochain_id("comptes")

    def enregistrer_compte(self, compte: CompteBancaire) -> None:
        """Ajoute le compte, ou le remplace s'il existe déjà (même id)."""
        ligne = _compte_vers_dict(compte)
        self._modifier(lambda donnees: _remplacer(donnees["comptes"], ligne))

    def supprimer_compte(self, compte_id: int) -> None:
        """Supprime le compte ; ses transactions restent dans l'historique."""

        def retirer(donnees: Ligne) -> None:
            donnees["comptes"] = [c for c in donnees["comptes"] if c["id"] != compte_id]

        self._modifier(retirer)

    def trouver_compte(self, compte_id: int) -> CompteBancaire | None:
        """Renvoie le compte qui a cet identifiant, ou None."""
        ligne = self._trouver("comptes", "id", compte_id)
        return _dict_vers_compte(ligne) if ligne else None

    def trouver_compte_par_iban(self, iban: str) -> CompteBancaire | None:
        """Renvoie le compte qui a cet IBAN (déjà normalisé), ou None."""
        ligne = self._trouver("comptes", "iban", iban)
        return _dict_vers_compte(ligne) if ligne else None

    def lister_comptes(
        self, proprietaire_id: int | None = None
    ) -> list[CompteBancaire]:
        """Renvoie les comptes d'un client, ou tous les comptes si None."""
        return [
            _dict_vers_compte(ligne)
            for ligne in self._donnees["comptes"]
            if proprietaire_id is None or ligne["proprietaire_id"] == proprietaire_id
        ]

    def prochain_id_transaction(self) -> int:
        """Réserve et renvoie un identifiant de transaction jamais attribué."""
        return self._prochain_id("transactions")

    def enregistrer_operation(
        self, comptes: list[CompteBancaire], transactions: list[Transaction]
    ) -> None:
        """Enregistre en une seule écriture les soldes modifiés et les transactions."""

        def appliquer(donnees: Ligne) -> None:
            for compte in comptes:
                _remplacer(donnees["comptes"], _compte_vers_dict(compte))
            donnees["transactions"].extend(
                _transaction_vers_dict(t) for t in transactions
            )

        self._modifier(appliquer)

    def lister_transactions(self, filtre: FiltreHistorique) -> list[Transaction]:
        """Renvoie les transactions qui répondent au filtre, dans l'ordre d'écriture."""
        transactions = map(_dict_vers_transaction, self._donnees["transactions"])
        return [t for t in transactions if filtre.accepte(t)]

    def _prochain_id(self, table: str) -> int:
        def incrementer(donnees: Ligne) -> None:
            donnees["compteurs"][table] += 1

        self._modifier(incrementer)
        identifiant: int = self._donnees["compteurs"][table]
        return identifiant

    def _trouver(self, table: str, cle: str, valeur: object) -> Ligne | None:
        for ligne in self._donnees[table]:
            if ligne[cle] == valeur:
                return dict(ligne)
        return None

    def _modifier(self, modification: Callable[[Ligne], None]) -> None:
        copie = copy.deepcopy(self._donnees)
        modification(copie)
        self._ecrire(copie)
        self._donnees = copie

    def _charger(self) -> Ligne:
        donnees: Ligne = {}
        if self._fichier.exists():
            with self._fichier.open(encoding="utf-8") as fichier:
                donnees = json.load(fichier)
        compteurs = donnees.setdefault("compteurs", {})
        for table in _TABLES:
            donnees.setdefault(table, [])
            compteurs.setdefault(table, 0)
        return donnees

    def _ecrire(self, donnees: Ligne) -> None:
        self._fichier.parent.mkdir(parents=True, exist_ok=True)
        temporaire = self._fichier.with_name(self._fichier.name + ".tmp")
        with temporaire.open("w", encoding="utf-8") as fichier:
            json.dump(donnees, fichier, ensure_ascii=False, indent=2)
        temporaire.replace(self._fichier)


def _remplacer(lignes: list[Ligne], nouvelle: Ligne) -> None:
    for position, ligne in enumerate(lignes):
        if ligne["id"] == nouvelle["id"]:
            lignes[position] = nouvelle
            return
    lignes.append(nouvelle)


def _utilisateur_vers_dict(utilisateur: User) -> Ligne:
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


def _dict_vers_utilisateur(ligne: Ligne) -> User:
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


def _compte_vers_dict(compte: CompteBancaire) -> Ligne:
    return {
        "id": compte.id,
        "proprietaire_id": compte.proprietaire_id,
        "iban": compte.iban,
        "type": compte.type,
        "solde": str(compte.solde),
        "statut": compte.statut.value,
        "date_creation": compte.date_creation.isoformat(),
    }


def _dict_vers_compte(ligne: Ligne) -> CompteBancaire:
    classe = classe_de_compte(ligne["type"])
    return classe(
        id=ligne["id"],
        proprietaire_id=ligne["proprietaire_id"],
        iban=ligne["iban"],
        date_creation=datetime.fromisoformat(ligne["date_creation"]),
        solde=Decimal(ligne["solde"]),
        statut=StatutCompte(ligne["statut"]),
    )


def _transaction_vers_dict(transaction: Transaction) -> Ligne:
    return {
        "id": transaction.id,
        "compte_source_id": transaction.compte_source_id,
        "compte_destinataire_id": transaction.compte_destinataire_id,
        "type": transaction.type.value,
        "montant": str(transaction.montant),
        "libelle": transaction.libelle,
        "date": transaction.date.isoformat(),
    }


def _dict_vers_transaction(ligne: Ligne) -> Transaction:
    return Transaction(
        id=ligne["id"],
        compte_source_id=ligne["compte_source_id"],
        compte_destinataire_id=ligne["compte_destinataire_id"],
        type=TypeTransaction(ligne["type"]),
        montant=Decimal(ligne["montant"]),
        libelle=ligne["libelle"],
        date=datetime.fromisoformat(ligne["date"]),
    )
