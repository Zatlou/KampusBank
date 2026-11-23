"""Bloc de saisie des informations personnelles (inscription et profil)."""

import tkinter as tk
from dataclasses import asdict
from tkinter import ttk

from kampusbank.service.formulaires import DonneesPersonnelles

_CHAMPS = [
    ("nom", "Nom"),
    ("prenom", "Prénom"),
    ("email", "Email"),
    ("telephone", "Téléphone"),
    ("adresse", "Adresse"),
    ("date_naissance", "Date de naissance (JJ/MM/AAAA)"),
]


class ChampsPersonnels(ttk.Frame):
    """Libellés et zones de saisie des informations personnelles.

    Avec avec_mot_de_passe, une ligne masquée est ajoutée (inscription).
    """

    def __init__(self, parent: tk.Misc, avec_mot_de_passe: bool = False) -> None:
        super().__init__(parent)
        self._variables: dict[str, tk.StringVar] = {}
        for ligne, (cle, libelle) in enumerate(_CHAMPS):
            self._variables[cle] = self._ajouter_ligne(ligne, libelle)
        self._mot_de_passe = (
            self._ajouter_ligne(len(_CHAMPS), "Mot de passe", masque=True)
            if avec_mot_de_passe
            else tk.StringVar(self)
        )
        self.columnconfigure(1, weight=1)

    def lire(self) -> DonneesPersonnelles:
        """Renvoie le texte saisi, sans le valider (c'est le rôle des services)."""
        return DonneesPersonnelles(
            **{cle: variable.get() for cle, variable in self._variables.items()}
        )

    def lire_mot_de_passe(self) -> str:
        """Renvoie le mot de passe saisi (vide sans ligne de mot de passe)."""
        return self._mot_de_passe.get()

    def remplir(self, donnees: DonneesPersonnelles) -> None:
        """Pré-remplit les champs (modification du profil)."""
        for cle, valeur in asdict(donnees).items():
            self._variables[cle].set(valeur)

    def _ajouter_ligne(
        self, ligne: int, libelle: str, masque: bool = False
    ) -> tk.StringVar:
        ttk.Label(self, text=libelle, style="Doux.TLabel").grid(
            row=ligne, column=0, sticky="w", padx=(0, 16), pady=5
        )
        variable = tk.StringVar(self)
        ttk.Entry(
            self, textvariable=variable, width=40, show="•" if masque else ""
        ).grid(row=ligne, column=1, sticky="ew", pady=5)
        return variable
