"""Comportement commun à toutes les vues."""

import tkinter as tk
from tkinter import ttk


class Vue(ttk.Frame):
    """Écran de l'application, avec une zone pour les messages d'erreur ou de succès."""

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self._message = ttk.Label(self, text="", wraplength=560, justify="center")

    def afficher_erreur(self, message: str) -> None:
        """Affiche un message d'erreur (en rouge)."""
        self._message.configure(text=message, style="Erreur.TLabel")

    def afficher_succes(self, message: str) -> None:
        """Affiche un message de confirmation (en vert)."""
        self._message.configure(text=message, style="Succes.TLabel")

    def _placer_message(self) -> None:
        self._message.pack(pady=8)
