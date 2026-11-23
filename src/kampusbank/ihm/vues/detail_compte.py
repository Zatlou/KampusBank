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

        self._entete(titre, "Détail du compte")

        fiche = ttk.Frame(self)
        fiche.pack(anchor="w")
        for ligne, (libelle, valeur) in enumerate(informations):
            ttk.Label(fiche, text=libelle, style="Doux.TLabel").grid(
                row=ligne, column=0, sticky="w", padx=(0, 24), pady=5
            )
            ttk.Label(fiche, text=valeur, style="Section.TLabel").grid(
                row=ligne, column=1, sticky="w", pady=5
            )

        self._placer_message()
        self._boutons(
            [
                ("Retour", on_retour, "TButton"),
                ("Supprimer ce compte", self._confirmer, "Danger.TButton"),
            ]
        )

    def _confirmer(self) -> None:
        if messagebox.askyesno(
            "Supprimer le compte", "Voulez-vous vraiment supprimer ce compte ?"
        ):
            self._on_supprimer()
