"""Écran de connexion."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from kampusbank.ihm.vues.base import Vue


class VueConnexion(Vue):
    """Saisie de l'email et du mot de passe."""

    def __init__(
        self,
        parent: tk.Misc,
        on_connexion: Callable[[str, str], None],
        on_inscription: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self._on_connexion = on_connexion
        self._email = tk.StringVar(self)
        self._mot_de_passe = tk.StringVar(self)

        ttk.Label(self, text="KampusBank", style="Titre.TLabel").pack(pady=(24, 4))
        ttk.Label(self, text="Connexion à votre espace").pack(pady=(0, 16))

        formulaire = ttk.Frame(self)
        formulaire.pack()
        ttk.Label(formulaire, text="Email").grid(
            row=0, column=0, sticky="w", padx=(0, 12), pady=4
        )
        champ_email = ttk.Entry(formulaire, textvariable=self._email, width=32)
        champ_email.grid(row=0, column=1, pady=4)
        ttk.Label(formulaire, text="Mot de passe").grid(
            row=1, column=0, sticky="w", padx=(0, 12), pady=4
        )
        champ_mot_de_passe = ttk.Entry(
            formulaire, textvariable=self._mot_de_passe, show="•", width=32
        )
        champ_mot_de_passe.grid(row=1, column=1, pady=4)

        self._placer_message()

        boutons = ttk.Frame(self)
        boutons.pack()
        ttk.Button(boutons, text="Se connecter", command=self._valider).pack(
            side="left", padx=4
        )
        ttk.Button(boutons, text="Créer un compte", command=on_inscription).pack(
            side="left", padx=4
        )

        champ_mot_de_passe.bind("<Return>", lambda _evenement: self._valider())
        champ_email.focus_set()

    def _valider(self) -> None:
        self._on_connexion(self._email.get(), self._mot_de_passe.get())
