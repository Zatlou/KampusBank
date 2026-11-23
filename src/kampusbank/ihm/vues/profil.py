"""Écran de modification du profil."""

import tkinter as tk
from collections.abc import Callable

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

        self._entete("Mon profil", "Modifiez vos informations personnelles.")

        self._champs = ChampsPersonnels(self)
        self._champs.remplir(informations)
        self._champs.pack(anchor="w")

        self._placer_message()
        self._boutons(
            [
                ("Enregistrer", self._valider, "Primaire.TButton"),
                ("Retour", on_retour, "TButton"),
            ]
        )

    def _valider(self) -> None:
        self._on_enregistrer(self._champs.lire())
