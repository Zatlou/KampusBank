"""Espace administrateur : RG2, recherche, blocage, suppression, RG13, statistiques."""

from decimal import Decimal

import pytest

from kampusbank.domaine.comptes import CompteBancaire
from kampusbank.domaine.exceptions import (
    AccesRefuseError,
    AnnulationImpossibleError,
    CompteBloqueError,
    SoldeInsuffisantError,
    SuppressionClientImpossibleError,
)
from kampusbank.domaine.transaction import TypeTransaction
from kampusbank.persistance.depot_json import DepotJson
from kampusbank.service.administration import ServiceAdministration
from kampusbank.service.authentification import ServiceAuthentification
from kampusbank.service.comptes import ServiceComptes
from kampusbank.service.operations import ServiceOperations
from tests.saisies import MOT_DE_PASSE_VALIDE, donnees_valides


class Banque:
    """Alice (courant + livret) et Bob (courant), puis connexion de l'admin."""

    def __init__(
        self,
        auth: ServiceAuthentification,
        comptes: ServiceComptes,
        operations: ServiceOperations,
    ) -> None:
        self.auth = auth
        auth.inscrire(donnees_valides(), MOT_DE_PASSE_VALIDE)
        auth.connecter("alice@exemple.fr", MOT_DE_PASSE_VALIDE)
        self.courant = comptes.ouvrir("COURANT")
        self.livret = comptes.ouvrir("LIVRET_A")
        operations.deposer(self.courant.id, "500")
        auth.inscrire(
            donnees_valides(nom="Martin", prenom="Bob", email="bob@exemple.fr"),
            MOT_DE_PASSE_VALIDE,
        )
        auth.connecter("bob@exemple.fr", MOT_DE_PASSE_VALIDE)
        self.compte_bob = comptes.ouvrir("COURANT")
        auth.creer_administrateur_initial(
            donnees_valides(email="admin@kampusbank.fr"), MOT_DE_PASSE_VALIDE
        )
        auth.connecter("admin@kampusbank.fr", MOT_DE_PASSE_VALIDE)


@pytest.fixture
def banque(
    auth: ServiceAuthentification,
    comptes: ServiceComptes,
    operations: ServiceOperations,
) -> Banque:
    return Banque(auth, comptes, operations)


def solde(depot: DepotJson, compte: CompteBancaire) -> Decimal:
    relu = depot.trouver_compte(compte.id)
    assert relu is not None
    return relu.solde


def test_rg2_un_client_n_a_pas_acces(
    banque: Banque, administration: ServiceAdministration
) -> None:
    banque.auth.connecter("bob@exemple.fr", MOT_DE_PASSE_VALIDE)
    with pytest.raises(AccesRefuseError):
        administration.statistiques()


class TestRecherche:
    def test_par_nom(
        self, banque: Banque, administration: ServiceAdministration
    ) -> None:
        resultat = administration.rechercher_clients(nom="martin")
        assert [c.email for c in resultat] == ["bob@exemple.fr"]

    def test_par_numero_de_compte(
        self, banque: Banque, administration: ServiceAdministration
    ) -> None:
        morceau = banque.livret.iban.replace("-", "")[-8:]
        resultat = administration.rechercher_clients(numero_compte=morceau)
        assert [c.email for c in resultat] == ["alice@exemple.fr"]

    def test_criteres_combines(
        self, banque: Banque, administration: ServiceAdministration
    ) -> None:
        assert administration.rechercher_clients(nom="alice", email="bob") == []
        assert len(administration.rechercher_clients(email="exemple.fr")) == 2


def test_bloquer_puis_debloquer(
    banque: Banque, administration: ServiceAdministration, operations: ServiceOperations
) -> None:
    assert administration.basculer_blocage(banque.courant.id).est_bloque
    banque.auth.connecter("alice@exemple.fr", MOT_DE_PASSE_VALIDE)
    with pytest.raises(CompteBloqueError):
        operations.deposer(banque.courant.id, "10")
    banque.auth.connecter("admin@kampusbank.fr", MOT_DE_PASSE_VALIDE)
    assert not administration.basculer_blocage(banque.courant.id).est_bloque


def test_modifier_un_client(
    banque: Banque, administration: ServiceAdministration
) -> None:
    bob = administration.rechercher_clients(email="bob")[0]
    administration.modifier_client(bob.id, donnees_valides(email="bob@neuf.fr"))
    assert administration.consulter_client(bob.id).email == "bob@neuf.fr"


class TestSuppressionClient:
    def test_refusee_si_un_compte_n_est_pas_vide(
        self, banque: Banque, administration: ServiceAdministration
    ) -> None:
        alice = administration.rechercher_clients(email="alice")[0]
        with pytest.raises(SuppressionClientImpossibleError):
            administration.supprimer_client(alice.id)

    def test_client_et_comptes_supprimes(
        self, banque: Banque, administration: ServiceAdministration, depot: DepotJson
    ) -> None:
        bob = administration.rechercher_clients(email="bob")[0]
        administration.supprimer_client(bob.id)
        assert administration.rechercher_clients(email="bob") == []
        assert depot.trouver_compte(banque.compte_bob.id) is None


class TestRG13Annulation:
    def test_annuler_un_depot(
        self, banque: Banque, administration: ServiceAdministration, depot: DepotJson
    ) -> None:
        administration.annuler_derniere_operation(banque.courant.id)

        assert solde(depot, banque.courant) == Decimal("0.00")
        types = [t.type for t in administration.historique_compte(banque.courant.id)]
        assert types == [TypeTransaction.ANNULATION, TypeTransaction.DEPOT]

    def test_annuler_un_virement_restaure_les_deux_comptes(
        self,
        banque: Banque,
        administration: ServiceAdministration,
        operations: ServiceOperations,
        depot: DepotJson,
    ) -> None:
        banque.auth.connecter("alice@exemple.fr", MOT_DE_PASSE_VALIDE)
        operations.virer_vers_iban(banque.courant.id, banque.compte_bob.iban, "200")
        banque.auth.connecter("admin@kampusbank.fr", MOT_DE_PASSE_VALIDE)

        administration.annuler_derniere_operation(banque.compte_bob.id)

        assert solde(depot, banque.courant) == Decimal("500.00")
        assert solde(depot, banque.compte_bob) == Decimal("0.00")

    def test_on_n_annule_pas_deux_fois(
        self, banque: Banque, administration: ServiceAdministration
    ) -> None:
        administration.annuler_derniere_operation(banque.courant.id)
        with pytest.raises(AnnulationImpossibleError):
            administration.annuler_derniere_operation(banque.courant.id)

    def test_compte_sans_operation(
        self, banque: Banque, administration: ServiceAdministration
    ) -> None:
        with pytest.raises(AnnulationImpossibleError):
            administration.annuler_derniere_operation(banque.livret.id)

    def test_annulation_impossible_si_l_argent_est_deja_parti(
        self,
        banque: Banque,
        administration: ServiceAdministration,
        operations: ServiceOperations,
        depot: DepotJson,
    ) -> None:
        banque.auth.connecter("alice@exemple.fr", MOT_DE_PASSE_VALIDE)
        operations.virer_vers_iban(banque.courant.id, banque.compte_bob.iban, "200")
        banque.auth.connecter("bob@exemple.fr", MOT_DE_PASSE_VALIDE)
        operations.retirer(banque.compte_bob.id, "150")
        banque.auth.connecter("admin@kampusbank.fr", MOT_DE_PASSE_VALIDE)

        with pytest.raises(SoldeInsuffisantError):
            administration.annuler_derniere_operation(banque.courant.id)
        assert solde(depot, banque.courant) == Decimal("300.00")


def test_statistiques(banque: Banque, administration: ServiceAdministration) -> None:
    stats = administration.statistiques()

    assert stats.nombre_clients == 2
    assert stats.nombre_comptes == 3
    assert stats.total_depots == Decimal("500.00")
    assert stats.total_soldes == Decimal("500.00")
