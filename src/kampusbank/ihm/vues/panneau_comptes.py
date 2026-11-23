"""Tableau de comptes avec les actions de l'administrateur."""

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk

from kampusbank.ihm.vues.tableau import Colonne, LigneTableau, Tableau

ActionCompte = Callable[[int], None]

COLONNES_COMPTES_ADMIN = [
    Colonne("Client", 150),
    Colonne("Type", 120),
    Colonne("IBAN", 270),
    Colonne("Solde", 110, "e"),
    Colonne("Statut", 80, "center"),
]


class PanneauComptes(ttk.Frame):
    """Comptes + boutons Bloquer/Débloquer, Historique et Annuler (RG13)."""

    def __init__(
        self,
        parent: tk.Misc,
        comptes: list[LigneTableau],
        on_bloquer: ActionCompte,
        on_historique: ActionCompte,
        on_annuler: ActionCompte,
        on_erreur: Callable[[str], None],
    ) -> None:
        super().__init__(parent)
        self._on_erreur = on_erreur
        self._tableau = Tableau(self, COLONNES_COMPTES_ADMIN, hauteur=7)
        self._tableau.remplir(comptes)
        self._tableau.sur_double_clic(on_historique)
        self._tableau.pack(fill="x")

        boutons = ttk.Frame(self)
        boutons.pack(anchor="w", pady=(6, 0))
        for texte, action, style in [
            ("Historique du compte", on_historique, "TButton"),
            ("Bloquer / Débloquer", on_bloquer, "TButton"),
            (
                "Annuler la dernière opération",
                self._confirmer(on_annuler),
                "Danger.TButton",
            ),
        ]:
            ttk.Button(
                boutons, text=texte, command=self._sur_selection(action), style=style
            ).pack(side="left", padx=(0, 10))

    def _sur_selection(self, action: ActionCompte) -> Callable[[], None]:
        def executer() -> None:
            compte_id = self._tableau.selection()
            if compte_id is None:
                self._on_erreur("Sélectionnez d'abord un compte dans le tableau.")
            else:
                action(compte_id)

        return executer

    @staticmethod
    def _confirmer(action: ActionCompte) -> ActionCompte:
        def executer(compte_id: int) -> None:
            if messagebox.askyesno(
                "Annuler une opération",
                "Annuler la dernière opération de ce compte ? Les soldes seront "
                "restaurés et l'annulation inscrite à l'historique.",
            ):
                action(compte_id)

        return executer
