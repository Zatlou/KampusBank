"""Tableau réutilisable : comptes du client, historique des transactions."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk
from typing import Literal, NamedTuple


class Colonne(NamedTuple):
    """Titre, largeur en pixels et alignement d'une colonne."""

    titre: str
    largeur: int
    alignement: Literal["w", "e", "center"] = "w"


class LigneTableau(NamedTuple):
    """Une ligne affichée : l'identifiant de l'objet et le texte de chaque colonne."""

    identifiant: int
    valeurs: tuple[str, ...]


class Tableau(ttk.Frame):
    """Tableau à colonnes avec barre de défilement ; une ligne peut être choisie."""

    def __init__(
        self, parent: tk.Misc, colonnes: list[Colonne], hauteur: int = 8
    ) -> None:
        super().__init__(parent)
        noms = [f"colonne{numero}" for numero in range(len(colonnes))]
        self._arbre = ttk.Treeview(
            self, columns=noms, show="headings", height=hauteur, selectmode="browse"
        )
        for nom, colonne in zip(noms, colonnes, strict=True):
            self._arbre.heading(nom, text=colonne.titre, anchor=colonne.alignement)
            self._arbre.column(nom, width=colonne.largeur, anchor=colonne.alignement)
        defilement = ttk.Scrollbar(self, orient="vertical", command=self._arbre.yview)
        self._arbre.configure(yscrollcommand=defilement.set)
        self._arbre.pack(side="left", fill="both", expand=True)
        defilement.pack(side="right", fill="y")

    def remplir(self, lignes: list[LigneTableau]) -> None:
        """Remplace le contenu du tableau."""
        self._arbre.delete(*self._arbre.get_children())
        for ligne in lignes:
            self._arbre.insert(
                "", "end", iid=str(ligne.identifiant), values=ligne.valeurs
            )

    def selection(self) -> int | None:
        """Identifiant de la ligne choisie, ou None."""
        choix = self._arbre.selection()
        return int(choix[0]) if choix else None

    def sur_double_clic(self, action: Callable[[int], object]) -> None:
        """Appelle l'action avec l'identifiant de la ligne double-cliquée."""

        def reagir(_evenement: object) -> None:
            identifiant = self.selection()
            if identifiant is not None:
                action(identifiant)

        self._arbre.bind("<Double-1>", reagir)
