"""Tableau de bord du client connecté : ses informations et ses comptes."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from kampusbank.ihm.vues.base import Vue
from kampusbank.ihm.vues.liste_de_choix import ListeDeChoix
from kampusbank.ihm.vues.tableau import Colonne, LigneTableau, Tableau
from kampusbank.service.formulaires import DonneesPersonnelles

_INFORMATIONS = [
    ("Nom", "nom"),
    ("Prénom", "prenom"),
    ("Email", "email"),
    ("Téléphone", "telephone"),
    ("Adresse", "adresse"),
    ("Naissance", "date_naissance"),
]

_COLONNES_COMPTES = [
    Colonne("Type", 160),
    Colonne("IBAN", 300),
    Colonne("Solde", 140, "e"),
    Colonne("Statut", 100, "center"),
]


class VueTableauDeBord(Vue):
    """Solde total, comptes, informations personnelles et accès aux opérations."""

    def __init__(
        self,
        parent: tk.Misc,
        informations: DonneesPersonnelles,
        comptes: list[LigneTableau],
        solde_total: str,
        types_de_compte: list[tuple[str, str]],
        on_ouvrir_compte: Callable[[str], None],
        on_detail: Callable[[int], None],
        on_operations: Callable[[], None],
        on_historique: Callable[[], None],
        on_profil: Callable[[], None],
        on_deconnexion: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self._on_ouvrir_compte = on_ouvrir_compte
        self._on_detail = on_detail

        self._entete(f"Bonjour {informations.prenom}", "Voici l'état de vos comptes.")
        self._tuiles([("Solde total", solde_total), ("Comptes", str(len(comptes)))])

        ttk.Label(self, text="Mes comptes", style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            self,
            text="Double-cliquez sur un compte pour voir son détail.",
            style="Etiquette.TLabel",
        ).pack(anchor="w")
        self._tableau = Tableau(self, _COLONNES_COMPTES, hauteur=5)
        self._tableau.remplir(comptes)
        self._tableau.sur_double_clic(on_detail)
        self._tableau.pack(fill="x", pady=(6, 10))

        ouverture = ttk.Frame(self)
        ouverture.pack(anchor="w")
        ttk.Label(ouverture, text="Ouvrir un compte :", style="Doux.TLabel").pack(
            side="left"
        )
        self._choix_type = ListeDeChoix(ouverture, types_de_compte, largeur=18)
        self._choix_type.pack(side="left", padx=8)
        ttk.Button(ouverture, text="Ouvrir", command=self._ouvrir).pack(side="left")

        self._placer_message()
        self._boutons(
            [
                ("Faire une opération", on_operations, "Primaire.TButton"),
                ("Historique", on_historique, "TButton"),
                ("Voir le détail", self._detail, "TButton"),
                ("Mon profil", on_profil, "TButton"),
                ("Se déconnecter", on_deconnexion, "TButton"),
            ]
        )

        ttk.Separator(self).pack(fill="x", pady=(18, 10))
        ttk.Label(self, text="Mes informations", style="Section.TLabel").pack(
            anchor="w"
        )
        bloc = ttk.Frame(self)
        bloc.pack(anchor="w", pady=(6, 0))
        for position, (libelle, attribut) in enumerate(_INFORMATIONS):
            ligne, colonne = divmod(position, 3)
            ttk.Label(bloc, text=libelle, style="Etiquette.TLabel").grid(
                row=ligne * 2, column=colonne, sticky="w", padx=(0, 40)
            )
            ttk.Label(bloc, text=getattr(informations, attribut)).grid(
                row=ligne * 2 + 1, column=colonne, sticky="w", padx=(0, 40), pady=(0, 8)
            )

    def _ouvrir(self) -> None:
        code = self._choix_type.valeur()
        if code is not None:
            self._on_ouvrir_compte(code)

    def _detail(self) -> None:
        compte_id = self._tableau.selection()
        if compte_id is None:
            self.afficher_erreur("Sélectionnez d'abord un compte dans le tableau.")
        else:
            self._on_detail(compte_id)
