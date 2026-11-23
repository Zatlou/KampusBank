"""Écran de modification du profil."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from kampusbank.ihm.vues.base import Vue
from kampusbank.ihm.vues.champs_personnels import ChampsPersonnels
from kampusbank.service.formulaires import DonneesPersonnelles


class VueProfil(Vue):
    """Formulaire pré-rempli des informations personnelles."""

    def __init__(
        self,
        parent: tk.Misc,
        informations: DonneesPersonnelles,
        on_enregistrer: Callable[[DonneesPersonnelles], None],
        on_retour: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self._on_enregistrer = on_enregistrer

        ttk.Label(self, text="Mon profil", style="Titre.TLabel").pack(pady=(0, 16))

        self._champs = ChampsPersonnels(self)
        self._champs.remplir(informations)
        self._champs.pack(fill="x")

        self._placer_message()

        boutons = ttk.Frame(self)
        boutons.pack()
        ttk.Button(boutons, text="Enregistrer", command=self._valider).pack(
            side="left", padx=4
        )
        ttk.Button(boutons, text="Retour", command=on_retour).pack(side="left", padx=4)

    def _valider(self) -> None:
        self._on_enregistrer(self._champs.lire())
