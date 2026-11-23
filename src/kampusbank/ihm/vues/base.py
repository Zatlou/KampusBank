"""Comportement commun à toutes les vues."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk
from typing import Literal

Ancre = Literal["w", "center"]
Bouton = tuple[str, Callable[[], object], str]


class Vue(ttk.Frame):
    """Écran de l'application, avec une zone pour les messages d'erreur ou de succès."""

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self._message = ttk.Label(self, text="", wraplength=760, justify="left")

    def afficher_erreur(self, message: str) -> None:
        """Affiche un message d'erreur (en rouge)."""
        self._message.configure(text=message, style="Erreur.TLabel")

    def afficher_succes(self, message: str) -> None:
        """Affiche un message de confirmation (en vert)."""
        self._message.configure(text=message, style="Succes.TLabel")

    def _entete(self, titre: str, sous_titre: str = "") -> None:
        ttk.Label(self, text=titre, style="Titre.TLabel").pack(anchor="w")
        if sous_titre:
            ttk.Label(self, text=sous_titre, style="Doux.TLabel").pack(anchor="w")
        ttk.Separator(self).pack(fill="x", pady=(10, 14))

    def _tuiles(self, chiffres: list[tuple[str, str]]) -> None:
        """Range des chiffres clés (libellé, valeur) dans des encadrés côte à côte."""
        rangee = ttk.Frame(self)
        rangee.pack(anchor="w", pady=(0, 16))
        for libelle, valeur in chiffres:
            tuile = ttk.Frame(rangee, style="Tuile.TFrame", padding=(18, 10))
            tuile.pack(side="left", padx=(0, 12))
            ttk.Label(tuile, text=valeur, style="TuileChiffre.TLabel").pack(anchor="w")
            ttk.Label(tuile, text=libelle, style="Tuile.TLabel").pack(anchor="w")

    def _placer_message(self, ancre: Ancre = "w") -> None:
        self._message.pack(anchor=ancre, pady=10)

    def _boutons(self, boutons: list[Bouton], ancre: Ancre = "w") -> ttk.Frame:
        rangee = ttk.Frame(self)
        rangee.pack(anchor=ancre, pady=(4, 0))
        for texte, action, style in boutons:
            ttk.Button(rangee, text=texte, command=action, style=style).pack(
                side="left", padx=(0, 10)
            )
        return rangee
