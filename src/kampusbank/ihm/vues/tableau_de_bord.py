"""Tableau de bord du client connecté."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from kampusbank.ihm.vues.base import Vue
from kampusbank.service.formulaires import DonneesPersonnelles

_LIBELLES = [
    ("Nom", "nom"),
    ("Prénom", "prenom"),
    ("Email", "email"),
    ("Téléphone", "telephone"),
    ("Adresse", "adresse"),
    ("Date de naissance", "date_naissance"),
]


class VueTableauDeBord(Vue):
    """Informations personnelles du client (ses comptes s'y ajoutent au jalon 2)."""

    def __init__(
        self,
        parent: tk.Misc,
        informations: DonneesPersonnelles,
        on_profil: Callable[[], None],
        on_deconnexion: Callable[[], None],
    ) -> None:
        super().__init__(parent)

        ttk.Label(
            self, text=f"Bonjour {informations.prenom}", style="Titre.TLabel"
        ).pack(anchor="w", pady=(0, 16))
        ttk.Label(self, text="Mes informations", style="Section.TLabel").pack(
            anchor="w", pady=(0, 8)
        )

        tableau = ttk.Frame(self)
        tableau.pack(anchor="w")
        for ligne, (libelle, attribut) in enumerate(_LIBELLES):
            ttk.Label(tableau, text=libelle).grid(
                row=ligne, column=0, sticky="w", padx=(0, 16), pady=2
            )
            ttk.Label(tableau, text=getattr(informations, attribut)).grid(
                row=ligne, column=1, sticky="w", pady=2
            )

        self._placer_message()

        boutons = ttk.Frame(self)
        boutons.pack(anchor="w", pady=(16, 0))
        ttk.Button(boutons, text="Modifier mon profil", command=on_profil).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(boutons, text="Se déconnecter", command=on_deconnexion).pack(
            side="left"
        )
