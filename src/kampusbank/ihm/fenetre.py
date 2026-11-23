"""Fenêtre principale de l'application."""

import tkinter as tk
from tkinter import ttk

from kampusbank.ihm.theme import appliquer_theme


class FenetrePrincipale:
    """Fenêtre unique : un bandeau fixe, puis un écran à la fois en dessous."""

    def __init__(self, titre: str) -> None:
        self._racine = tk.Tk()
        self._racine.title(titre)
        self._racine.geometry("980x780")
        self._racine.minsize(880, 680)
        appliquer_theme(self._racine)

        bandeau = ttk.Frame(self._racine, style="Bandeau.TFrame", padding=(32, 14))
        bandeau.pack(fill="x")
        ttk.Label(bandeau, text=titre, style="Bandeau.TLabel").pack(side="left")
        ttk.Label(
            bandeau, text="Votre banque, simplement", style="BandeauDoux.TLabel"
        ).pack(side="left", padx=16, pady=(6, 0))
        self._ecran: ttk.Frame | None = None

    @property
    def conteneur(self) -> tk.Tk:
        """Widget parent dans lequel les vues sont créées."""
        return self._racine

    def afficher(self, ecran: ttk.Frame) -> None:
        """Remplace l'écran affiché (sous le bandeau) par celui-ci."""
        if self._ecran is not None:
            self._ecran.destroy()
        self._ecran = ecran
        ecran.pack(fill="both", expand=True, padx=40, pady=(20, 24))

    def lancer(self) -> None:
        """Affiche la fenêtre au premier plan et attend jusqu'à sa fermeture."""
        self._racine.lift()
        self._racine.attributes("-topmost", True)
        self._racine.after_idle(self._racine.attributes, "-topmost", False)
        self._racine.focus_force()
        self._racine.mainloop()
