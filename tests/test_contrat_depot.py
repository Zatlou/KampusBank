"""EC6 : le même contrat est vérifié sur le dépôt JSON et sur le dépôt MySQL.

Les tests MySQL ne tournent qu'avec KAMPUSBANK_TEST_MYSQL=1 : chaque test crée
une base kampusbank_test_xxxx avec sql/creation.sql, puis la supprime (EC9).
Sans cette variable, ils sont ignorés et pytest passe sur une machine sans MySQL.
"""

import os
import uuid
from collections.abc import Iterator
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pymysql
import pytest

from kampusbank.config.parametres import charger_parametres
from kampusbank.domaine.comptes import CompteCourant, LivretA, StatutCompte
from kampusbank.domaine.historique import FiltreHistorique
from kampusbank.domaine.transaction import Transaction, TypeTransaction
from kampusbank.persistance.depot import Depot
from kampusbank.persistance.depot_json import DepotJson
from kampusbank.persistance.depot_mysql import DepotMySQL, executer_script
from kampusbank.service.administration import ServiceAdministration
from kampusbank.service.authentification import ServiceAuthentification
from kampusbank.service.comptes import ServiceComptes
from kampusbank.service.operations import ServiceOperations
from tests.fabriques import utilisateur_valide
from tests.saisies import MOT_DE_PASSE_VALIDE, donnees_valides

RACINE = Path(__file__).resolve().parents[1]
JOUR = datetime(2026, 11, 23, 10, 30, 15, 123456)


@pytest.fixture(params=["json", "mysql"])
def depot(request: pytest.FixtureRequest, tmp_path: Path) -> Iterator[Depot]:
    if request.param == "json":
        yield DepotJson(tmp_path / "donnees.json")
        return
    mysql = charger_parametres(RACINE / "kampusbank.toml").persistance.mysql
    if os.environ.get("KAMPUSBANK_TEST_MYSQL") != "1" or mysql is None:
        pytest.skip("MySQL non testé : relancer avec KAMPUSBANK_TEST_MYSQL=1")
    base = f"kampusbank_test_{uuid.uuid4().hex[:8]}"
    serveur = pymysql.connect(
        host=mysql.hote,
        port=mysql.port,
        user=mysql.utilisateur,
        password=mysql.mot_de_passe,
    )
    with serveur.cursor() as curseur:
        curseur.execute(f"CREATE DATABASE {base}")
    executer_script(
        mysql.hote,
        mysql.port,
        mysql.utilisateur,
        mysql.mot_de_passe,
        base,
        RACINE / "sql" / "creation.sql",
    )
    depot_mysql = DepotMySQL(
        mysql.hote, mysql.port, mysql.utilisateur, mysql.mot_de_passe, base
    )
    try:
        yield depot_mysql
    finally:
        depot_mysql.fermer()
        with serveur.cursor() as curseur:
            curseur.execute(f"DROP DATABASE {base}")
        serveur.close()


def livret(solde: str = "0.10") -> LivretA:
    return LivretA(
        id=1,
        proprietaire_id=1,
        iban="FR76-KPBK-1234-5678-9012-3456-789",
        date_creation=JOUR,
        solde=Decimal(solde),
    )


def courant(compte_id: int, solde: str) -> CompteCourant:
    return CompteCourant(
        id=compte_id,
        proprietaire_id=1,
        iban=f"FR76-KPBK-0000-0000-0000-0000-{compte_id:03d}",
        date_creation=JOUR,
        solde=Decimal(solde),
    )


def virement(
    numero: int, source: int, destination: int, jour: int
) -> list[Transaction]:
    moment = datetime(2026, 11, jour, 12, 0)
    return [
        Transaction(
            id=numero + decalage,
            compte_source_id=source,
            compte_destinataire_id=destination,
            type=type_operation,
            montant=Decimal("25.00"),
            date=moment,
            libelle="Loyer",
        )
        for decalage, type_operation in enumerate(
            [TypeTransaction.VIREMENT_EMIS, TypeTransaction.VIREMENT_RECU]
        )
    ]


def test_un_utilisateur_est_relu_a_l_identique(depot: Depot) -> None:
    utilisateur = utilisateur_valide()
    utilisateur.enregistrer_echec_connexion(JOUR, 1, timedelta(minutes=15))
    depot.enregistrer_utilisateur(utilisateur)

    relu = depot.trouver_utilisateur_par_email("alice@exemple.fr")

    assert relu is not None
    assert relu.nom_complet == utilisateur.nom_complet
    assert relu.date_naissance == utilisateur.date_naissance
    assert relu.bloque_jusqu_a == utilisateur.bloque_jusqu_a
    assert relu.admin is False
    assert depot.trouver_utilisateur(utilisateur.id) is not None
    assert len(depot.lister_utilisateurs()) == 1


def test_les_identifiants_ne_sont_jamais_reattribues(depot: Depot) -> None:
    assert [depot.prochain_id_compte() for _ in range(3)] == [1, 2, 3]
    assert depot.prochain_id_utilisateur() == 1
    assert depot.prochain_id_transaction() == 1


def test_un_compte_est_relu_avec_son_type_et_son_solde_exact(depot: Depot) -> None:
    depot.enregistrer_utilisateur(utilisateur_valide())
    compte = livret()
    compte.bloquer()
    depot.enregistrer_compte(compte)

    relu = depot.trouver_compte_par_iban(compte.iban)

    assert isinstance(relu, LivretA)
    assert relu.solde == Decimal("0.10")
    assert relu.statut is StatutCompte.BLOQUE
    assert relu.date_creation == JOUR
    assert [c.id for c in depot.lister_comptes(proprietaire_id=1)] == [1]


def test_operation_puis_historique_filtre(depot: Depot) -> None:
    depot.enregistrer_utilisateur(utilisateur_valide())
    depot.enregistrer_operation(
        [courant(1, "75.00"), courant(2, "25.00")], virement(1, 1, 2, jour=10)
    )
    depot.enregistrer_operation(
        [courant(1, "50.00"), courant(2, "50.00")], virement(3, 1, 2, jour=20)
    )

    du_compte_2 = depot.lister_transactions(FiltreHistorique(frozenset({2})))
    emis_en_debut_de_mois = depot.lister_transactions(
        FiltreHistorique(
            frozenset({1, 2}),
            type=TypeTransaction.VIREMENT_EMIS,
            au=datetime(2026, 11, 15).date(),
        )
    )

    assert [t.id for t in du_compte_2] == [2, 4]
    assert [t.id for t in emis_en_debut_de_mois] == [1]
    compte_1 = depot.trouver_compte(1)
    assert compte_1 is not None
    assert compte_1.solde == Decimal("50.00")


def test_supprimer_un_compte_garde_son_historique(depot: Depot) -> None:
    depot.enregistrer_utilisateur(utilisateur_valide())
    depot.enregistrer_operation(
        [courant(1, "75.00"), courant(2, "25.00")], virement(1, 1, 2, jour=10)
    )
    depot.supprimer_compte(2)

    assert depot.trouver_compte(2) is None
    assert len(depot.lister_transactions(FiltreHistorique(frozenset({2})))) == 1


def test_supprimer_un_utilisateur_supprime_ses_comptes(depot: Depot) -> None:
    depot.enregistrer_utilisateur(utilisateur_valide())
    depot.enregistrer_compte(livret())
    depot.supprimer_utilisateur(1)

    assert depot.trouver_utilisateur(1) is None
    assert depot.lister_comptes() == []


def test_les_services_marchent_sans_savoir_quel_depot_ils_utilisent(
    auth: ServiceAuthentification,
    comptes: ServiceComptes,
    operations: ServiceOperations,
    administration: ServiceAdministration,
    depot: Depot,
) -> None:
    auth.inscrire(donnees_valides(), MOT_DE_PASSE_VALIDE)
    auth.connecter("alice@exemple.fr", MOT_DE_PASSE_VALIDE)
    source, epargne = comptes.ouvrir("COURANT"), comptes.ouvrir("LIVRET_A")
    operations.deposer(source.id, "200")
    operations.virer_entre_mes_comptes(source.id, epargne.id, "80")
    auth.creer_administrateur_initial(
        donnees_valides(email="admin@kampusbank.fr"), MOT_DE_PASSE_VALIDE
    )
    auth.connecter("admin@kampusbank.fr", MOT_DE_PASSE_VALIDE)
    administration.annuler_derniere_operation(epargne.id)

    relu = depot.trouver_compte(source.id)
    assert relu is not None
    assert relu.solde == Decimal("200.00")
    assert administration.statistiques().total_depots == Decimal("200.00")


def test_mysql_annule_toute_l_operation_si_une_ecriture_echoue(depot: Depot) -> None:
    if not isinstance(depot, DepotMySQL):
        pytest.skip("contrôle propre à la base MySQL")
    depot.enregistrer_utilisateur(utilisateur_valide())
    depot.enregistrer_operation(
        [courant(1, "75.00"), courant(2, "25.00")], virement(1, 1, 2, jour=10)
    )

    with pytest.raises(pymysql.err.OperationalError):
        depot.enregistrer_operation(
            [courant(1, "0.00"), courant(2, "-1.00")], virement(3, 1, 2, jour=11)
        )

    compte_1 = depot.trouver_compte(1)
    assert compte_1 is not None
    assert compte_1.solde == Decimal("75.00")
    assert len(depot.lister_transactions(FiltreHistorique(frozenset({1})))) == 1
