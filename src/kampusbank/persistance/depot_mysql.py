"""Persistance dans une base MySQL (facultative, choisie dans kampusbank.toml)."""

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Any

import pymysql
from pymysql.cursors import DictCursor

from kampusbank.domaine.comptes import CompteBancaire, StatutCompte, classe_de_compte
from kampusbank.domaine.historique import FiltreHistorique
from kampusbank.domaine.transaction import Transaction, TypeTransaction
from kampusbank.domaine.user import User
from kampusbank.persistance.depot import Depot

Ligne = dict[str, Any]

_COLONNES_UTILISATEUR = (
    "id, nom, prenom, email, telephone, adresse, date_naissance, "
    "mot_de_passe_hash, admin, echecs_connexion, bloque_jusqu_a"
)


class DepotMySQL(Depot):
    """Mêmes services que DepotJson, mais les données vivent dans MySQL.

    Chaque méthode s'exécute dans une transaction SQL : elle est validée
    (COMMIT) si tout s'est bien passé, annulée (ROLLBACK) sinon. Un virement
    écrit ses deux soldes et ses deux transactions dans la même transaction
    SQL : c'est la base elle-même qui garantit RG11.
    Toutes les valeurs passent par des paramètres (%s), jamais par
    concaténation de texte : aucune injection SQL n'est possible.
    """

    def __init__(
        self, hote: str, port: int, utilisateur: str, mot_de_passe: str, base: str
    ) -> None:
        self._connexion = pymysql.connect(
            host=hote,
            port=port,
            user=utilisateur,
            password=mot_de_passe,
            database=base,
            charset="utf8mb4",
            autocommit=False,
            cursorclass=DictCursor,
        )

    def fermer(self) -> None:
        """Ferme la connexion à la base."""
        self._connexion.close()

    def prochain_id_utilisateur(self) -> int:
        """Réserve et renvoie un identifiant d'utilisateur jamais attribué."""
        return self._prochain_id("utilisateurs")

    def enregistrer_utilisateur(self, utilisateur: User) -> None:
        """Ajoute l'utilisateur, ou le remplace s'il existe déjà (même id)."""
        with self._transaction() as curseur:
            curseur.execute(
                f"INSERT INTO users ({_COLONNES_UTILISATEUR}) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) AS nouveau "
                "ON DUPLICATE KEY UPDATE nom = nouveau.nom, prenom = nouveau.prenom, "
                "email = nouveau.email, telephone = nouveau.telephone, "
                "adresse = nouveau.adresse, date_naissance = nouveau.date_naissance, "
                "mot_de_passe_hash = nouveau.mot_de_passe_hash, admin = nouveau.admin, "
                "echecs_connexion = nouveau.echecs_connexion, "
                "bloque_jusqu_a = nouveau.bloque_jusqu_a",
                (
                    utilisateur.id,
                    utilisateur.nom,
                    utilisateur.prenom,
                    utilisateur.email,
                    utilisateur.telephone,
                    utilisateur.adresse,
                    utilisateur.date_naissance,
                    utilisateur.mot_de_passe_hash,
                    utilisateur.admin,
                    utilisateur.echecs_connexion,
                    utilisateur.bloque_jusqu_a,
                ),
            )

    def trouver_utilisateur_par_email(self, email: str) -> User | None:
        """Renvoie l'utilisateur qui a cet email (déjà normalisé), ou None."""
        lignes = self._lire(
            f"SELECT {_COLONNES_UTILISATEUR} FROM users WHERE email = %s", (email,)
        )
        return _ligne_vers_utilisateur(lignes[0]) if lignes else None

    def trouver_utilisateur(self, utilisateur_id: int) -> User | None:
        """Renvoie l'utilisateur qui a cet identifiant, ou None."""
        lignes = self._lire(
            f"SELECT {_COLONNES_UTILISATEUR} FROM users WHERE id = %s",
            (utilisateur_id,),
        )
        return _ligne_vers_utilisateur(lignes[0]) if lignes else None

    def lister_utilisateurs(self) -> list[User]:
        """Renvoie tous les utilisateurs, administrateurs compris."""
        lignes = self._lire(f"SELECT {_COLONNES_UTILISATEUR} FROM users ORDER BY id")
        return [_ligne_vers_utilisateur(ligne) for ligne in lignes]

    def supprimer_utilisateur(self, utilisateur_id: int) -> None:
        """Supprime l'utilisateur ; ses comptes suivent (ON DELETE CASCADE)."""
        with self._transaction() as curseur:
            curseur.execute("DELETE FROM users WHERE id = %s", (utilisateur_id,))

    def prochain_id_compte(self) -> int:
        """Réserve et renvoie un identifiant de compte jamais attribué."""
        return self._prochain_id("comptes")

    def enregistrer_compte(self, compte: CompteBancaire) -> None:
        """Ajoute le compte, ou le remplace s'il existe déjà (même id)."""
        with self._transaction() as curseur:
            _ecrire_compte(curseur, compte)

    def supprimer_compte(self, compte_id: int) -> None:
        """Supprime le compte ; ses transactions restent dans l'historique."""
        with self._transaction() as curseur:
            curseur.execute("DELETE FROM comptes_bancaires WHERE id = %s", (compte_id,))

    def trouver_compte(self, compte_id: int) -> CompteBancaire | None:
        """Renvoie le compte qui a cet identifiant, ou None."""
        lignes = self._lire(
            "SELECT * FROM comptes_bancaires WHERE id = %s", (compte_id,)
        )
        return _ligne_vers_compte(lignes[0]) if lignes else None

    def trouver_compte_par_iban(self, iban: str) -> CompteBancaire | None:
        """Renvoie le compte qui a cet IBAN (déjà normalisé), ou None."""
        lignes = self._lire("SELECT * FROM comptes_bancaires WHERE iban = %s", (iban,))
        return _ligne_vers_compte(lignes[0]) if lignes else None

    def lister_comptes(
        self, proprietaire_id: int | None = None
    ) -> list[CompteBancaire]:
        """Renvoie les comptes d'un client, ou tous les comptes si None."""
        if proprietaire_id is None:
            lignes = self._lire("SELECT * FROM comptes_bancaires ORDER BY id")
        else:
            lignes = self._lire(
                "SELECT * FROM comptes_bancaires WHERE proprietaire_id = %s "
                "ORDER BY id",
                (proprietaire_id,),
            )
        return [_ligne_vers_compte(ligne) for ligne in lignes]

    def prochain_id_transaction(self) -> int:
        """Réserve et renvoie un identifiant de transaction jamais attribué."""
        return self._prochain_id("transactions")

    def enregistrer_operation(
        self, comptes: list[CompteBancaire], transactions: list[Transaction]
    ) -> None:
        """Écrit soldes et transactions dans une seule transaction SQL (RG11)."""
        with self._transaction() as curseur:
            for compte in comptes:
                _ecrire_compte(curseur, compte)
            for transaction in transactions:
                curseur.execute(
                    "INSERT INTO transactions (id, compte_source_id, "
                    "compte_destinataire_id, type, montant, libelle, `date`) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (
                        transaction.id,
                        transaction.compte_source_id,
                        transaction.compte_destinataire_id,
                        transaction.type.value,
                        transaction.montant,
                        transaction.libelle,
                        transaction.date,
                    ),
                )

    def lister_transactions(self, filtre: FiltreHistorique) -> list[Transaction]:
        """Renvoie les transactions qui répondent au filtre, dans l'ordre d'écriture.

        La requête SQL fait le gros du tri (comptes, type, période) ; le filtre
        du domaine tranche ensuite quel compte est concerné par chaque ligne,
        pour que cette règle ne soit écrite qu'à un seul endroit.
        """
        if not filtre.comptes_ids:
            return []
        comptes = sorted(filtre.comptes_ids)
        marques = ", ".join(["%s"] * len(comptes))
        requete = (
            "SELECT * FROM transactions WHERE (compte_source_id IN "
            f"({marques}) OR compte_destinataire_id IN ({marques}))"
        )
        parametres: list[Any] = [*comptes, *comptes]
        if filtre.type is not None:
            requete += " AND type = %s"
            parametres.append(filtre.type.value)
        if filtre.du is not None:
            requete += " AND `date` >= %s"
            parametres.append(datetime.combine(filtre.du, time.min))
        if filtre.au is not None:
            requete += " AND `date` < %s"
            parametres.append(datetime.combine(filtre.au + timedelta(days=1), time.min))
        transactions = map(
            _ligne_vers_transaction, self._lire(requete + " ORDER BY id", parametres)
        )
        return [t for t in transactions if filtre.accepte(t)]

    def _prochain_id(self, entite: str) -> int:
        with self._transaction() as curseur:
            curseur.execute(
                "UPDATE compteurs SET valeur = LAST_INSERT_ID(valeur + 1) "
                "WHERE entite = %s",
                (entite,),
            )
            curseur.execute("SELECT LAST_INSERT_ID() AS valeur")
            ligne = curseur.fetchone()
        assert ligne is not None
        return int(ligne["valeur"])

    def _lire(self, requete: str, parametres: Sequence[Any] = ()) -> list[Ligne]:
        with self._transaction() as curseur:
            curseur.execute(requete, parametres)
            return list(curseur.fetchall())

    @contextmanager
    def _transaction(self) -> Iterator[DictCursor]:
        curseur = self._connexion.cursor()
        try:
            yield curseur
            self._connexion.commit()
        except Exception:
            self._connexion.rollback()
            raise
        finally:
            curseur.close()


def executer_script(
    hote: str,
    port: int,
    utilisateur: str,
    mot_de_passe: str,
    base: str,
    script: Path,
) -> None:
    """Exécute un fichier .sql simple (instructions séparées par des « ; »)."""
    lignes = [
        ligne
        for ligne in script.read_text(encoding="utf-8").splitlines()
        if not ligne.strip().startswith("--")
    ]
    instructions = [i.strip() for i in "\n".join(lignes).split(";") if i.strip()]
    connexion = pymysql.connect(
        host=hote, port=port, user=utilisateur, password=mot_de_passe, database=base
    )
    try:
        with connexion.cursor() as curseur:
            for instruction in instructions:
                curseur.execute(instruction)
        connexion.commit()
    finally:
        connexion.close()


def _ecrire_compte(curseur: DictCursor, compte: CompteBancaire) -> None:
    curseur.execute(
        "INSERT INTO comptes_bancaires (id, proprietaire_id, iban, type, solde, "
        "statut, date_creation) VALUES (%s, %s, %s, %s, %s, %s, %s) AS nouveau "
        "ON DUPLICATE KEY UPDATE solde = nouveau.solde, statut = nouveau.statut",
        (
            compte.id,
            compte.proprietaire_id,
            compte.iban,
            compte.type,
            compte.solde,
            compte.statut.value,
            compte.date_creation,
        ),
    )


def _ligne_vers_utilisateur(ligne: Ligne) -> User:
    return User(
        id=ligne["id"],
        nom=ligne["nom"],
        prenom=ligne["prenom"],
        email=ligne["email"],
        telephone=ligne["telephone"],
        adresse=ligne["adresse"],
        date_naissance=ligne["date_naissance"],
        mot_de_passe_hash=ligne["mot_de_passe_hash"],
        admin=bool(ligne["admin"]),
        echecs_connexion=ligne["echecs_connexion"],
        bloque_jusqu_a=ligne["bloque_jusqu_a"],
    )


def _ligne_vers_compte(ligne: Ligne) -> CompteBancaire:
    classe = classe_de_compte(ligne["type"])
    return classe(
        id=ligne["id"],
        proprietaire_id=ligne["proprietaire_id"],
        iban=ligne["iban"],
        date_creation=ligne["date_creation"],
        solde=ligne["solde"],
        statut=StatutCompte(ligne["statut"]),
    )


def _ligne_vers_transaction(ligne: Ligne) -> Transaction:
    return Transaction(
        id=ligne["id"],
        compte_source_id=ligne["compte_source_id"],
        compte_destinataire_id=ligne["compte_destinataire_id"],
        type=TypeTransaction(ligne["type"]),
        montant=ligne["montant"],
        libelle=ligne["libelle"],
        date=ligne["date"],
    )
