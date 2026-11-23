"""Contrôleur des opérations bancaires et de l'historique."""

from collections.abc import Callable

from kampusbank.domaine.exceptions import KampusBankError
from kampusbank.domaine.transaction import Transaction
from kampusbank.domaine.validation import formater_montant
from kampusbank.ihm.fenetre import FenetrePrincipale
from kampusbank.ihm.routeur import Ecran, Routeur
from kampusbank.ihm.vues.historique import VueHistorique
from kampusbank.ihm.vues.operations import VueOperations
from kampusbank.ihm.vues.tableau import LigneTableau
from kampusbank.service.comptes import ServiceComptes
from kampusbank.service.operations import ServiceOperations


class ControleurOperations:
    """Transmet les opérations saisies au service et affiche le résultat."""

    def __init__(
        self,
        fenetre: FenetrePrincipale,
        routeur: Routeur,
        service_comptes: ServiceComptes,
        service_operations: ServiceOperations,
    ) -> None:
        self._fenetre = fenetre
        self._routeur = routeur
        self._comptes = service_comptes
        self._operations = service_operations

    def afficher_operations(self) -> None:
        """Affiche les onglets Dépôt, Retrait et Virement."""
        comptes = self._choix_des_comptes()
        if comptes is None:
            return
        operations = self._operations
        vue = VueOperations(
            self._fenetre.conteneur,
            comptes=comptes,
            on_depot=lambda compte, montant, libelle: self._executer(
                vue, lambda: operations.deposer(compte, montant, libelle), "Dépôt"
            ),
            on_retrait=lambda compte, montant, libelle: self._executer(
                vue, lambda: operations.retirer(compte, montant, libelle), "Retrait"
            ),
            on_virement=lambda source, destination, montant, libelle: self._executer(
                vue,
                lambda: operations.virer_entre_mes_comptes(
                    source, destination, montant, libelle
                ),
                "Virement",
            ),
            on_virement_iban=lambda source, iban, montant, libelle: self._executer(
                vue,
                lambda: operations.virer_vers_iban(source, iban, montant, libelle),
                "Virement",
            ),
            on_retour=lambda: self._routeur.aller_a(Ecran.TABLEAU_DE_BORD),
        )
        self._fenetre.afficher(vue)

    def afficher_historique(self) -> None:
        """Affiche l'historique de tous les comptes, sans filtre au départ."""
        comptes = self._choix_des_comptes()
        if comptes is None:
            return
        vue = VueHistorique(
            self._fenetre.conteneur,
            comptes=comptes,
            types_operation=self._operations.types_operation(),
            on_filtrer=lambda compte, type_operation, du, au: self._filtrer(
                vue, compte, type_operation or "", du, au
            ),
            on_retour=lambda: self._routeur.aller_a(Ecran.TABLEAU_DE_BORD),
        )
        self._fenetre.afficher(vue)
        self._filtrer(vue, None, "", "", "")

    def _executer(
        self, vue: VueOperations, operation: Callable[[], Transaction], nom: str
    ) -> None:
        try:
            transaction = operation()
        except KampusBankError as erreur:
            vue.afficher_erreur(str(erreur))
            return
        vue.vider_saisies()
        vue.afficher_succes(
            f"{nom} de {formater_montant(transaction.montant)} enregistré."
        )

    def _filtrer(
        self,
        vue: VueHistorique,
        compte_id: int | None,
        type_operation: str,
        du: str,
        au: str,
    ) -> None:
        try:
            transactions = self._operations.historique(
                compte_id, type_operation, du, au
            )
            ibans = {compte.id: compte.iban for compte in self._comptes.lister()}
        except KampusBankError as erreur:
            vue.afficher_erreur(str(erreur))
            return
        vue.afficher_lignes([_ligne(t, ibans) for t in transactions])

    def _choix_des_comptes(self) -> list[tuple[int, str]] | None:
        try:
            comptes = self._comptes.lister()
        except KampusBankError:
            self._routeur.aller_a(Ecran.CONNEXION)
            return None
        return [(c.id, f"{c.libelle} — {c.iban}") for c in comptes]


def _ligne(transaction: Transaction, ibans: dict[int, str]) -> LigneTableau:
    signe = "+" if transaction.est_credit else "−"
    return LigneTableau(
        transaction.id,
        (
            f"{transaction.date:%d/%m/%Y %H:%M}",
            ibans.get(transaction.compte_concerne_id, "compte supprimé"),
            transaction.type.libelle,
            transaction.libelle,
            f"{signe} {formater_montant(transaction.montant)}",
        ),
        "credit" if transaction.est_credit else "debit",
    )
