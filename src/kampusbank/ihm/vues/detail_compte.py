"""Détail d'un compte : solde, type, IBAN, date de création."""

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk

from kampusbank.ihm.vues.base import Vue


class VueDetailCompte(Vue):
    """Fiche d'un compte, avec sa suppression (refusée si le solde n'est pas nul)."""

    def __init__(
        self,
        parent: tk.Misc,
        titre: str,
        informations: list[tuple[str, str]],
        on_supprimer: Callable[[], None],
        on_retour: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self._on_supprimer = on_supprimer

        ttk.Label(self, text=titre, style="Titre.TLabel").pack(anchor="w", pady=(0, 16))

        fiche = ttk.Frame(self)
        fiche.pack(anchor="w")
        for ligne, (libelle, valeur) in enumerate(informations):
            ttk.Label(fiche, text=f"{libelle} :").grid(
                row=ligne, column=0, sticky="w", padx=(0, 16), pady=3
            )
            ttk.Label(fiche, text=valeur).grid(row=ligne, column=1, sticky="w", pady=3)

        self._placer_message()

        boutons = ttk.Frame(self)
        boutons.pack(anchor="w")
        ttk.Button(boutons, text="Supprimer ce compte", command=self._confirmer).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(boutons, text="Retour", command=on_retour).pack(side="left")

    def _confirmer(self) -> None:
        if messagebox.askyesno(
            "Supprimer le compte", "Voulez-vous vraiment supprimer ce compte ?"
        ):
            self._on_supprimer()
