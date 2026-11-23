"""Historique des transactions, filtrable par compte, type et période."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from kampusbank.ihm.vues.base import Vue
from kampusbank.ihm.vues.liste_de_choix import ListeDeChoix
from kampusbank.ihm.vues.tableau import Colonne, LigneTableau, Tableau

ActionFiltre = Callable[[int | None, str | None, str, str], None]

_COLONNES = [
    Colonne("Date", 130),
    Colonne("Compte", 260),
    Colonne("Opération", 120),
    Colonne("Libellé", 150),
    Colonne("Montant", 110, "e"),
]


class VueHistorique(Vue):
    """Filtres en haut, transactions en dessous (les plus récentes d'abord)."""

    def __init__(
        self,
        parent: tk.Misc,
        comptes: list[tuple[int, str]],
        types_operation: list[tuple[str, str]],
        on_filtrer: ActionFiltre,
        on_retour: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self._on_filtrer = on_filtrer

        self._entete(
            "Historique", "Vos opérations, des plus récentes aux plus anciennes."
        )

        filtres = ttk.Frame(self)
        filtres.pack(anchor="w")
        ttk.Label(filtres, text="Compte", style="Doux.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self._compte: ListeDeChoix[int | None] = ListeDeChoix(
            filtres, [(None, "Tous mes comptes"), *comptes], largeur=44
        )
        self._compte.grid(row=0, column=1, sticky="w", padx=(8, 16), pady=2)
        ttk.Label(filtres, text="Opération", style="Doux.TLabel").grid(
            row=0, column=2, sticky="w"
        )
        self._type: ListeDeChoix[str | None] = ListeDeChoix(
            filtres, [(None, "Toutes"), *types_operation], largeur=14
        )
        self._type.grid(row=0, column=3, sticky="w", padx=8, pady=2)

        ttk.Label(filtres, text="Du (JJ/MM/AAAA)", style="Doux.TLabel").grid(
            row=1, column=0, sticky="w"
        )
        self._du = tk.StringVar(self)
        ttk.Entry(filtres, textvariable=self._du, width=12).grid(
            row=1, column=1, sticky="w", padx=(8, 16), pady=2
        )
        ttk.Label(filtres, text="Au", style="Doux.TLabel").grid(
            row=1, column=2, sticky="w"
        )
        self._au = tk.StringVar(self)
        ttk.Entry(filtres, textvariable=self._au, width=12).grid(
            row=1, column=3, sticky="w", padx=8, pady=2
        )
        ttk.Button(
            filtres, text="Filtrer", command=self._filtrer, style="Primaire.TButton"
        ).grid(row=1, column=4, sticky="w")

        self._tableau = Tableau(self, _COLONNES, hauteur=12)
        self._tableau.pack(fill="both", expand=True, pady=(12, 0))

        self._placer_message()
        ttk.Button(self, text="Retour", command=on_retour).pack(anchor="w")

    def afficher_lignes(self, lignes: list[LigneTableau]) -> None:
        """Remplace les transactions affichées."""
        self._tableau.remplir(lignes)
        self.afficher_succes(f"{len(lignes)} opération(s).")

    def _filtrer(self) -> None:
        self._on_filtrer(
            self._compte.valeur(), self._type.valeur(), self._du.get(), self._au.get()
        )
