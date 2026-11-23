"""Accueil de l'espace administrateur : statistiques, recherche et clients."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from kampusbank.ihm.vues.base import Vue
from kampusbank.ihm.vues.tableau import Colonne, LigneTableau, Tableau

_COLONNES = [
    Colonne("Nom", 130),
    Colonne("Prénom", 120),
    Colonne("Email", 230),
    Colonne("Téléphone", 110),
    Colonne("Comptes", 70, "center"),
]


class VueAccueilAdmin(Vue):
    """Chiffres clés, recherche combinée et liste des clients."""

    def __init__(
        self,
        parent: tk.Misc,
        statistiques: list[tuple[str, str]],
        clients: list[LigneTableau],
        on_rechercher: Callable[[str, str, str], None],
        on_client: Callable[[int], object],
        on_comptes: Callable[[], object],
        on_deconnexion: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self._on_rechercher = on_rechercher
        self._on_client = on_client

        self._entete("Espace administrateur", "Supervision des clients et des comptes.")
        self._tuiles(statistiques)

        ttk.Label(self, text="Rechercher un client", style="Section.TLabel").pack(
            anchor="w"
        )
        recherche = ttk.Frame(self)
        recherche.pack(anchor="w", pady=(4, 8))
        self._criteres: list[tk.StringVar] = []
        for colonne, libelle in enumerate(["Nom", "Email", "N° de compte (IBAN)"]):
            ttk.Label(recherche, text=libelle, style="Etiquette.TLabel").grid(
                row=0, column=colonne, sticky="w"
            )
            variable = tk.StringVar(self)
            ttk.Entry(recherche, textvariable=variable, width=22).grid(
                row=1, column=colonne, sticky="w", padx=(0, 8)
            )
            self._criteres.append(variable)
        ttk.Button(
            recherche,
            text="Rechercher",
            command=self._rechercher,
            style="Primaire.TButton",
        ).grid(row=1, column=3)
        ttk.Button(recherche, text="Tout afficher", command=self._tout).grid(
            row=1, column=4, padx=(8, 0)
        )

        self._tableau = Tableau(self, _COLONNES, hauteur=9)
        self._tableau.remplir(clients)
        self._tableau.sur_double_clic(on_client)
        self._tableau.pack(fill="x")

        self._placer_message()

        self._boutons(
            [
                ("Fiche du client", self._fiche, "Primaire.TButton"),
                ("Tous les comptes", on_comptes, "TButton"),
                ("Se déconnecter", on_deconnexion, "TButton"),
            ]
        )

    def afficher_clients(self, clients: list[LigneTableau]) -> None:
        """Remplace la liste des clients (résultat d'une recherche)."""
        self._tableau.remplir(clients)
        self.afficher_succes(f"{len(clients)} client(s) trouvé(s).")

    def _rechercher(self) -> None:
        nom, email, compte = (variable.get() for variable in self._criteres)
        self._on_rechercher(nom, email, compte)

    def _tout(self) -> None:
        for variable in self._criteres:
            variable.set("")
        self._on_rechercher("", "", "")

    def _fiche(self) -> None:
        client_id = self._tableau.selection()
        if client_id is None:
            self.afficher_erreur("Sélectionnez d'abord un client dans le tableau.")
        else:
            self._on_client(client_id)
