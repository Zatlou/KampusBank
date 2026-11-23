"""Accueil de l'espace administrateur (complété au jalon 3)."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from kampusbank.ihm.vues.base import Vue
from kampusbank.service.formulaires import DonneesPersonnelles

_COLONNES = [
    ("nom", "Nom", 140),
    ("prenom", "Prénom", 140),
    ("email", "Email", 240),
    ("telephone", "Téléphone", 120),
]


class VueAccueilAdmin(Vue):
    """Liste des clients de la banque."""

    def __init__(
        self,
        parent: tk.Misc,
        clients: list[DonneesPersonnelles],
        on_deconnexion: Callable[[], None],
    ) -> None:
        super().__init__(parent)

        ttk.Label(self, text="Espace administrateur", style="Titre.TLabel").pack(
            anchor="w", pady=(0, 16)
        )
        ttk.Label(self, text=f"Clients ({len(clients)})", style="Section.TLabel").pack(
            anchor="w", pady=(0, 8)
        )

        tableau = ttk.Treeview(
            self, columns=[cle for cle, _, _ in _COLONNES], show="headings", height=12
        )
        for cle, titre, largeur in _COLONNES:
            tableau.heading(cle, text=titre)
            tableau.column(cle, width=largeur)
        for client in clients:
            tableau.insert(
                "", "end", values=[getattr(client, cle) for cle, _, _ in _COLONNES]
            )
        tableau.pack(fill="both", expand=True)

        self._placer_message()

        ttk.Button(self, text="Se déconnecter", command=on_deconnexion).pack(
            anchor="w", pady=(8, 0)
        )
