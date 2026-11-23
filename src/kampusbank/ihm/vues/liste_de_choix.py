"""Liste déroulante qui renvoie une valeur (identifiant, code) plutôt qu'un texte."""

import tkinter as tk
from tkinter import ttk


class ListeDeChoix[T](ttk.Combobox):
    """Liste déroulante en lecture seule : libellés affichés, valeurs lues."""

    def __init__(
        self, parent: tk.Misc, options: list[tuple[T, str]], largeur: int = 40
    ) -> None:
        super().__init__(
            parent,
            state="readonly",
            width=largeur,
            values=[libelle for _, libelle in options],
        )
        self._choix = options
        if options:
            self.current(0)

    def valeur(self) -> T | None:
        """Valeur de l'option choisie, ou None si la liste est vide."""
        position = self.current()
        if position < 0:
            return None
        return self._choix[position][0]
