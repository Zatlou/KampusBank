"""Écran d'inscription d'un nouveau client."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from kampusbank.ihm.vues.base import Vue
from kampusbank.ihm.vues.champs_personnels import ChampsPersonnels
from kampusbank.service.formulaires import DonneesPersonnelles


class VueInscription(Vue):
    """Formulaire de création de compte client."""

    def __init__(
        self,
        parent: tk.Misc,
        on_inscription: Callable[[DonneesPersonnelles, str], None],
        on_retour: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self._on_inscription = on_inscription

        ttk.Label(self, text="Créer un compte", style="Titre.TLabel").pack(pady=(0, 16))

        self._champs = ChampsPersonnels(self, avec_mot_de_passe=True)
        self._champs.pack(fill="x")
        ttk.Label(
            self, text="Au moins 8 caractères, dont une majuscule et un chiffre."
        ).pack(anchor="e")

        self._placer_message()

        boutons = ttk.Frame(self)
        boutons.pack()
        ttk.Button(boutons, text="Créer mon compte", command=self._valider).pack(
            side="left", padx=4
        )
        ttk.Button(boutons, text="Retour", command=on_retour).pack(side="left", padx=4)

    def _valider(self) -> None:
        self._on_inscription(self._champs.lire(), self._champs.lire_mot_de_passe())
