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

        self._entete(
            "Créer un compte", "Quelques informations pour ouvrir votre espace client."
        )

        self._champs = ChampsPersonnels(self, avec_mot_de_passe=True)
        self._champs.pack(anchor="w")
        ttk.Label(
            self,
            text="Mot de passe : 8 caractères, dont une majuscule et un chiffre.",
            style="Etiquette.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        self._placer_message()
        self._boutons(
            [
                ("Créer mon compte", self._valider, "Primaire.TButton"),
                ("Retour", on_retour, "TButton"),
            ]
        )

    def _valider(self) -> None:
        self._on_inscription(self._champs.lire(), self._champs.lire_mot_de_passe())
