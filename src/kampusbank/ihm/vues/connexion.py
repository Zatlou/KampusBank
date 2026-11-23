"""Écran de connexion."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from kampusbank.ihm.vues.base import Vue


class VueConnexion(Vue):
    """Saisie de l'email et du mot de passe, au centre de l'écran."""

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

        bloc = ttk.Frame(self)
        bloc.pack(expand=True)

        ttk.Label(bloc, text="Connexion", style="Titre.TLabel").pack(anchor="w")
        ttk.Label(
            bloc,
            text="Accédez à votre espace client ou administrateur.",
            style="Doux.TLabel",
        ).pack(anchor="w", pady=(2, 20))

        ttk.Label(bloc, text="Email", style="Etiquette.TLabel").pack(anchor="w")
        champ_email = ttk.Entry(bloc, textvariable=self._email, width=36)
        champ_email.pack(fill="x", pady=(2, 12))
        ttk.Label(bloc, text="Mot de passe", style="Etiquette.TLabel").pack(anchor="w")
        champ_mot_de_passe = ttk.Entry(
            bloc, textvariable=self._mot_de_passe, show="•", width=36
        )
        champ_mot_de_passe.pack(fill="x", pady=(2, 18))

        ttk.Button(
            bloc, text="Se connecter", style="Primaire.TButton", command=self._valider
        ).pack(fill="x")
        ttk.Button(bloc, text="Créer un compte", command=on_inscription).pack(
            fill="x", pady=(8, 0)
        )

        self._message = ttk.Label(bloc, text="", wraplength=340, justify="left")
        self._message.pack(anchor="w", pady=12)

        champ_mot_de_passe.bind("<Return>", lambda _evenement: self._valider())
        champ_email.focus_set()

    def _valider(self) -> None:
        self._on_connexion(self._email.get(), self._mot_de_passe.get())
