"""EC2 (hiérarchie), EC3 (encapsulation), RG6, RG7 et règles propres à chaque type."""

from datetime import datetime
from decimal import Decimal

import pytest

from kampusbank.domaine import comptes as module_comptes
from kampusbank.domaine.comptes import (
    PEL,
    CompteBancaire,
    CompteCourant,
    LivretA,
    StatutCompte,
    classe_de_compte,
    types_de_compte,
)
from kampusbank.domaine.exceptions import (
    CompteBloqueError,
    CompteNonVideError,
    PlafondDepasseError,
    RetraitInterditError,
    SoldeInsuffisantError,
    TypeCompteInconnuError,
)


def nouveau(classe: type[CompteBancaire], solde: str = "0.00") -> CompteBancaire:
    return classe(
        id=1,
        proprietaire_id=1,
        iban="FR76-KPBK-0000-0000-0000-0000-001",
        date_creation=datetime(2026, 11, 23),
        solde=Decimal(solde),
    )


class TestEC2Hierarchie:
    def test_la_classe_abstraite_ne_s_instancie_pas(self) -> None:
        with pytest.raises(TypeError):
            CompteBancaire(  # type: ignore[abstract]
                id=1, proprietaire_id=1, iban="x", date_creation=datetime(2026, 1, 1)
            )

    def test_les_trois_types_sont_inscrits(self) -> None:
        assert [c.CODE for c in types_de_compte()] == ["COURANT", "LIVRET_A", "PEL"]
        assert classe_de_compte("PEL") is PEL

    def test_type_inconnu_refuse(self) -> None:
        with pytest.raises(TypeCompteInconnuError):
            classe_de_compte("ASSURANCE_VIE")

    def test_ajouter_un_type_suffit_d_ecrire_une_sous_classe(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            module_comptes, "_TYPES_DE_COMPTE", dict(module_comptes._TYPES_DE_COMPTE)
        )

        class LivretJeune(CompteBancaire):
            CODE = "LIVRET_JEUNE"
            LIBELLE = "Livret Jeune"

            @property
            def plafond(self) -> Decimal | None:
                return Decimal("1600.00")

        assert classe_de_compte("LIVRET_JEUNE") is LivretJeune
        assert nouveau(LivretJeune).type == "LIVRET_JEUNE"


class TestEC3Encapsulation:
    def test_solde_nul_et_compte_actif_a_l_ouverture(self) -> None:
        compte = nouveau(CompteCourant)
        assert compte.solde == Decimal("0.00")
        assert compte.statut is StatutCompte.ACTIF

    def test_le_solde_ne_s_ecrit_pas_directement(self) -> None:
        compte = nouveau(CompteCourant)
        with pytest.raises(AttributeError):
            compte.solde = Decimal("1000000")  # type: ignore[misc]

    def test_crediter_puis_debiter(self) -> None:
        compte = nouveau(CompteCourant)
        compte.crediter(Decimal("100.00"))
        compte.debiter(Decimal("30.50"))
        assert compte.solde == Decimal("69.50")

    def test_un_debit_ne_rend_jamais_le_solde_negatif(self) -> None:
        compte = nouveau(CompteCourant, "50.00")
        with pytest.raises(SoldeInsuffisantError):
            compte.debiter(Decimal("50.01"))
        assert compte.solde == Decimal("50.00")


class TestRG6Suppression:
    def test_compte_non_vide_refuse(self) -> None:
        with pytest.raises(CompteNonVideError):
            nouveau(CompteCourant, "0.01").verifier_suppression()

    def test_compte_vide_accepte(self) -> None:
        nouveau(CompteCourant).verifier_suppression()


class TestRG7CompteBloque:
    def test_ni_credit_ni_debit(self) -> None:
        compte = nouveau(CompteCourant, "100.00")
        compte.bloquer()
        with pytest.raises(CompteBloqueError):
            compte.crediter(Decimal("10.00"))
        with pytest.raises(CompteBloqueError):
            compte.debiter(Decimal("10.00"))
        assert compte.solde == Decimal("100.00")

    def test_debloque_il_fonctionne_a_nouveau(self) -> None:
        compte = nouveau(CompteCourant)
        compte.bloquer()
        compte.debloquer()
        compte.crediter(Decimal("10.00"))
        assert compte.solde == Decimal("10.00")


class TestReglesParType:
    def test_compte_courant_sans_plafond(self) -> None:
        compte = nouveau(CompteCourant)
        compte.crediter(Decimal("1000000.00"))
        assert compte.plafond is None

    def test_livret_a_plafonne(self) -> None:
        compte = nouveau(LivretA)
        compte.crediter(Decimal("22950.00"))
        with pytest.raises(PlafondDepasseError):
            compte.crediter(Decimal("0.01"))

    def test_pel_plafonne(self) -> None:
        compte = nouveau(PEL, "61200.00")
        with pytest.raises(PlafondDepasseError):
            compte.crediter(Decimal("1.00"))

    def test_pel_refuse_les_retraits_mais_pas_les_virements(self) -> None:
        compte = nouveau(PEL, "500.00")
        with pytest.raises(RetraitInterditError):
            compte.retirer(Decimal("100.00"))
        compte.debiter(Decimal("100.00"))
        assert compte.solde == Decimal("400.00")

    def test_retrait_sur_livret_a_autorise(self) -> None:
        compte = nouveau(LivretA, "500.00")
        compte.retirer(Decimal("100.00"))
        assert compte.solde == Decimal("400.00")
