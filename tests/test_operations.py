"""RG7 à RG12 : dépôts, retraits, virements atomiques et historique."""

from decimal import Decimal

import pytest

from kampusbank.domaine.comptes import CompteBancaire
from kampusbank.domaine.exceptions import (
    CompteBloqueError,
    CompteIntrouvableError,
    DateInvalideError,
    IbanInvalideError,
    LimiteOperationError,
    MontantInvalideError,
    PlafondDepasseError,
    RetraitInterditError,
    SoldeInsuffisantError,
    VirementInvalideError,
)
from kampusbank.domaine.transaction import TypeTransaction
from kampusbank.domaine.user import User
from kampusbank.persistance.depot_json import DepotJson
from kampusbank.service.authentification import ServiceAuthentification
from kampusbank.service.comptes import ServiceComptes
from kampusbank.service.operations import ServiceOperations
from tests.fabriques import HorlogeFactice
from tests.saisies import MOT_DE_PASSE_VALIDE, donnees_valides


def solde(depot: DepotJson, compte: CompteBancaire) -> Decimal:
    relu = depot.trouver_compte(compte.id)
    assert relu is not None
    return relu.solde


def types_historique(operations: ServiceOperations) -> list[TypeTransaction]:
    return [t.type for t in operations.historique()]


@pytest.fixture
def courant(comptes: ServiceComptes, alice: User) -> CompteBancaire:
    return comptes.ouvrir("COURANT")


@pytest.fixture
def livret(comptes: ServiceComptes, alice: User) -> CompteBancaire:
    return comptes.ouvrir("LIVRET_A")


class TestRG8Depot:
    def test_depot_credite_et_s_inscrit(
        self, operations: ServiceOperations, depot: DepotJson, courant: CompteBancaire
    ) -> None:
        operations.deposer(courant.id, "150,50", "Salaire")

        assert solde(depot, courant) == Decimal("150.50")
        assert types_historique(operations) == [TypeTransaction.DEPOT]

    def test_moins_de_un_euro_refuse(
        self, operations: ServiceOperations, courant: CompteBancaire
    ) -> None:
        with pytest.raises(LimiteOperationError):
            operations.deposer(courant.id, "0,99")

    def test_rg17_saisie_invalide_refusee(
        self, operations: ServiceOperations, courant: CompteBancaire
    ) -> None:
        with pytest.raises(MontantInvalideError):
            operations.deposer(courant.id, "dix euros")

    def test_montants_exacts(
        self, operations: ServiceOperations, depot: DepotJson, courant: CompteBancaire
    ) -> None:
        operations.deposer(courant.id, "1,10")
        operations.deposer(courant.id, "2,20")

        assert 1.10 + 2.20 != 3.30
        assert solde(depot, courant) == Decimal("3.30")


class TestRG9Retrait:
    def test_retrait_debite(
        self, operations: ServiceOperations, depot: DepotJson, courant: CompteBancaire
    ) -> None:
        operations.deposer(courant.id, "500")
        operations.retirer(courant.id, "120")

        assert solde(depot, courant) == Decimal("380.00")

    def test_plus_de_mille_euros_refuse(
        self, operations: ServiceOperations, courant: CompteBancaire
    ) -> None:
        operations.deposer(courant.id, "5000")
        with pytest.raises(LimiteOperationError):
            operations.retirer(courant.id, "1000,01")

    def test_solde_jamais_negatif(
        self, operations: ServiceOperations, depot: DepotJson, courant: CompteBancaire
    ) -> None:
        operations.deposer(courant.id, "50")
        with pytest.raises(SoldeInsuffisantError):
            operations.retirer(courant.id, "50,01")
        assert solde(depot, courant) == Decimal("50.00")

    def test_pas_de_retrait_sur_un_pel(
        self, operations: ServiceOperations, comptes: ServiceComptes, alice: User
    ) -> None:
        pel = comptes.ouvrir("PEL")
        operations.deposer(pel.id, "100")
        with pytest.raises(RetraitInterditError):
            operations.retirer(pel.id, "10")


class TestRG7CompteBloque:
    def test_aucune_operation_sur_un_compte_bloque(
        self, operations: ServiceOperations, depot: DepotJson, courant: CompteBancaire
    ) -> None:
        courant.bloquer()
        depot.enregistrer_compte(courant)

        with pytest.raises(CompteBloqueError):
            operations.deposer(courant.id, "10")
        with pytest.raises(CompteBloqueError):
            operations.retirer(courant.id, "10")


class TestRG10RG11Virement:
    def test_virement_entre_mes_comptes(
        self,
        operations: ServiceOperations,
        depot: DepotJson,
        courant: CompteBancaire,
        livret: CompteBancaire,
    ) -> None:
        operations.deposer(courant.id, "300")
        operations.virer_entre_mes_comptes(courant.id, livret.id, "100", "Épargne")

        assert solde(depot, courant) == Decimal("200.00")
        assert solde(depot, livret) == Decimal("100.00")
        assert types_historique(operations)[:2] == [
            TypeTransaction.VIREMENT_RECU,
            TypeTransaction.VIREMENT_EMIS,
        ]

    def test_virement_vers_un_autre_client_par_iban(
        self,
        operations: ServiceOperations,
        comptes: ServiceComptes,
        auth: ServiceAuthentification,
        depot: DepotJson,
        alice: User,
    ) -> None:
        auth.inscrire(donnees_valides(email="bob@exemple.fr"), MOT_DE_PASSE_VALIDE)
        auth.connecter("bob@exemple.fr", MOT_DE_PASSE_VALIDE)
        compte_bob = comptes.ouvrir("COURANT")
        auth.connecter("alice@exemple.fr", MOT_DE_PASSE_VALIDE)
        compte_alice = comptes.ouvrir("COURANT")
        operations.deposer(compte_alice.id, "80")

        iban_tape = compte_bob.iban.replace("-", " ").lower()
        operations.virer_vers_iban(compte_alice.id, iban_tape, "30")

        assert solde(depot, compte_alice) == Decimal("50.00")
        assert solde(depot, compte_bob) == Decimal("30.00")

    def test_solde_insuffisant_rien_ne_change(
        self,
        operations: ServiceOperations,
        depot: DepotJson,
        courant: CompteBancaire,
        livret: CompteBancaire,
    ) -> None:
        operations.deposer(courant.id, "20")
        with pytest.raises(SoldeInsuffisantError):
            operations.virer_entre_mes_comptes(courant.id, livret.id, "20,01")

        assert solde(depot, courant) == Decimal("20.00")
        assert solde(depot, livret) == Decimal("0.00")
        assert types_historique(operations) == [TypeTransaction.DEPOT]

    def test_rg11_destination_refusee_la_source_n_est_pas_debitee(
        self,
        operations: ServiceOperations,
        depot: DepotJson,
        courant: CompteBancaire,
        livret: CompteBancaire,
    ) -> None:
        operations.deposer(courant.id, "30000")
        with pytest.raises(PlafondDepasseError):
            operations.virer_entre_mes_comptes(courant.id, livret.id, "25000")

        assert solde(depot, courant) == Decimal("30000.00")
        assert solde(depot, livret) == Decimal("0.00")

    def test_rg11_destination_bloquee_la_source_n_est_pas_debitee(
        self,
        operations: ServiceOperations,
        depot: DepotJson,
        courant: CompteBancaire,
        livret: CompteBancaire,
    ) -> None:
        operations.deposer(courant.id, "100")
        livret.bloquer()
        depot.enregistrer_compte(livret)

        with pytest.raises(CompteBloqueError):
            operations.virer_entre_mes_comptes(courant.id, livret.id, "50")
        assert solde(depot, courant) == Decimal("100.00")

    def test_meme_compte_refuse(
        self, operations: ServiceOperations, courant: CompteBancaire
    ) -> None:
        operations.deposer(courant.id, "100")
        with pytest.raises(VirementInvalideError):
            operations.virer_entre_mes_comptes(courant.id, courant.id, "10")

    def test_iban_inconnu_ou_mal_forme(
        self, operations: ServiceOperations, courant: CompteBancaire
    ) -> None:
        operations.deposer(courant.id, "100")
        with pytest.raises(CompteIntrouvableError):
            operations.virer_vers_iban(
                courant.id, "FR76-KPBK-0000-0000-0000-0000-000", "10"
            )
        with pytest.raises(IbanInvalideError):
            operations.virer_vers_iban(courant.id, "FR00 1234", "10")

    def test_pas_de_virement_depuis_le_compte_d_un_autre(
        self,
        operations: ServiceOperations,
        auth: ServiceAuthentification,
        courant: CompteBancaire,
        livret: CompteBancaire,
    ) -> None:
        operations.deposer(courant.id, "100")
        auth.inscrire(donnees_valides(email="bob@exemple.fr"), MOT_DE_PASSE_VALIDE)
        auth.connecter("bob@exemple.fr", MOT_DE_PASSE_VALIDE)

        with pytest.raises(CompteIntrouvableError):
            operations.virer_vers_iban(courant.id, livret.iban, "10")


class TestRG12Historique:
    def test_seules_les_operations_reussies_sont_inscrites(
        self, operations: ServiceOperations, courant: CompteBancaire
    ) -> None:
        operations.deposer(courant.id, "100")
        with pytest.raises(SoldeInsuffisantError):
            operations.retirer(courant.id, "500")
        operations.retirer(courant.id, "40")

        assert types_historique(operations) == [
            TypeTransaction.RETRAIT,
            TypeTransaction.DEPOT,
        ]

    def test_filtre_par_compte_et_par_type(
        self,
        operations: ServiceOperations,
        courant: CompteBancaire,
        livret: CompteBancaire,
    ) -> None:
        operations.deposer(courant.id, "100")
        operations.deposer(livret.id, "50")
        operations.retirer(courant.id, "10")

        du_livret = operations.historique(compte_id=livret.id)
        retraits = operations.historique(type_operation="RETRAIT")

        assert [t.montant for t in du_livret] == [Decimal("50.00")]
        assert [t.montant for t in retraits] == [Decimal("10.00")]

    def test_filtre_par_periode(
        self,
        operations: ServiceOperations,
        horloge: HorlogeFactice,
        courant: CompteBancaire,
    ) -> None:
        operations.deposer(courant.id, "10")
        horloge.avancer(minutes=2 * 24 * 60)
        operations.deposer(courant.id, "20")

        resultat = operations.historique(du="25/11/2026", au="25/11/2026")

        assert [t.montant for t in resultat] == [Decimal("20.00")]

    def test_periode_a_l_envers_refusee(
        self, operations: ServiceOperations, alice: User
    ) -> None:
        with pytest.raises(DateInvalideError):
            operations.historique(du="30/11/2026", au="01/11/2026")
