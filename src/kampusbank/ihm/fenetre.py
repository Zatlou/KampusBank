"""Fenêtre principale de l'application."""

import tkinter as tk
from tkinter import ttk


class FenetrePrincipale:
    """Fenêtre unique : les contrôleurs y affichent un écran à la fois."""

    def __init__(self, titre: str) -> None:
        self._racine = tk.Tk()
        self._racine.title(titre)
        self._racine.geometry("760x580")
        self._racine.minsize(640, 480)
        style = ttk.Style(self._racine)
        style.configure("Titre.TLabel", font=("Helvetica", 20, "bold"))
        style.configure("Section.TLabel", font=("Helvetica", 14, "bold"))
        style.configure("Erreur.TLabel", foreground="#b3261e")
        style.configure("Succes.TLabel", foreground="#1e7b34")
        self._ecran: ttk.Frame | None = None

    @property
    def conteneur(self) -> tk.Tk:
        """Widget parent dans lequel les vues sont créées."""
        return self._racine

    def afficher(self, ecran: ttk.Frame) -> None:
        """Remplace l'écran affiché par celui-ci."""
        if self._ecran is not None:
            self._ecran.destroy()
        self._ecran = ecran
        ecran.pack(fill="both", expand=True, padx=32, pady=24)

    def lancer(self) -> None:
        """Démarre la boucle d'événements jusqu'à la fermeture de la fenêtre."""
        self._racine.mainloop()
