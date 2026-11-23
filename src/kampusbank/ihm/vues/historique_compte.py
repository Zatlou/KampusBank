"""Historique d'un compte vu par l'administrateur."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from kampusbank.ihm.vues.base import Vue
from kampusbank.ihm.vues.tableau import Colonne, LigneTableau, Tableau

_COLONNES = [
    Colonne("Date", 130),
    Colonne("Opération", 120),
    Colonne("Libellé", 280),
    Colonne("Montant", 120, "e"),
]


class VueHistoriqueCompte(Vue):
    """Transactions d'un compte, les plus récentes d'abord."""

    def __init__(
        self,
        parent: tk.Misc,
        titre: str,
        lignes: list[LigneTableau],
        on_retour: Callable[[], object],
    ) -> None:
        super().__init__(parent)
        self._entete(titre, "Opérations du compte, les plus récentes d'abord.")
        tableau = Tableau(self, _COLONNES, hauteur=14)
        tableau.remplir(lignes)
        tableau.pack(fill="both", expand=True)
        self._placer_message()
        ttk.Button(self, text="Retour", command=on_retour).pack(anchor="w")
