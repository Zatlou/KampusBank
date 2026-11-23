"""Liste de tous les comptes de la banque (administrateur)."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from kampusbank.ihm.vues.base import Vue
from kampusbank.ihm.vues.panneau_comptes import ActionCompte, PanneauComptes
from kampusbank.ihm.vues.tableau import LigneTableau


class VueComptesAdmin(Vue):
    """Tous les comptes, avec blocage, historique et annulation."""

    def __init__(
        self,
        parent: tk.Misc,
        comptes: list[LigneTableau],
        on_bloquer: ActionCompte,
        on_historique: ActionCompte,
        on_annuler: ActionCompte,
        on_retour: Callable[[], object],
    ) -> None:
        super().__init__(parent)
        ttk.Label(self, text="Tous les comptes", style="Titre.TLabel").pack(
            anchor="w", pady=(0, 12)
        )
        PanneauComptes(
            self, comptes, on_bloquer, on_historique, on_annuler, self.afficher_erreur
        ).pack(fill="x")
        self._placer_message()
        ttk.Button(self, text="Retour", command=on_retour).pack(anchor="w")
