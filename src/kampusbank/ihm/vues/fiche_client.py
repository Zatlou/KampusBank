"""Fiche d'un client vue par l'administrateur : informations et comptes."""

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk

from kampusbank.ihm.vues.base import Vue
from kampusbank.ihm.vues.champs_personnels import ChampsPersonnels
from kampusbank.ihm.vues.panneau_comptes import ActionCompte, PanneauComptes
from kampusbank.ihm.vues.tableau import LigneTableau
from kampusbank.service.formulaires import DonneesPersonnelles


class VueFicheClient(Vue):
    """Modification, suppression du client et actions sur ses comptes."""

    def __init__(
        self,
        parent: tk.Misc,
        titre: str,
        informations: DonneesPersonnelles,
        comptes: list[LigneTableau],
        on_enregistrer: Callable[[DonneesPersonnelles], None],
        on_supprimer: Callable[[], None],
        on_bloquer: ActionCompte,
        on_historique: ActionCompte,
        on_annuler: ActionCompte,
        on_retour: Callable[[], object],
    ) -> None:
        super().__init__(parent)
        self._on_enregistrer = on_enregistrer
        self._on_supprimer = on_supprimer

        self._entete(titre, "Fiche client")

        self._champs = ChampsPersonnels(self)
        self._champs.remplir(informations)
        self._champs.pack(anchor="w")
        self._boutons(
            [
                ("Enregistrer les modifications", self._valider, "Primaire.TButton"),
                ("Supprimer le client", self._confirmer, "Danger.TButton"),
            ]
        )
        ttk.Separator(self).pack(fill="x", pady=(14, 10))

        ttk.Label(self, text="Comptes du client", style="Section.TLabel").pack(
            anchor="w"
        )
        PanneauComptes(
            self, comptes, on_bloquer, on_historique, on_annuler, self.afficher_erreur
        ).pack(fill="x", pady=(4, 0))

        self._placer_message()
        ttk.Button(self, text="Retour", command=on_retour).pack(anchor="w")

    def _valider(self) -> None:
        self._on_enregistrer(self._champs.lire())

    def _confirmer(self) -> None:
        if messagebox.askyesno(
            "Supprimer le client",
            "Supprimer définitivement ce client et ses comptes (tous à 0,00 €) ?",
        ):
            self._on_supprimer()
