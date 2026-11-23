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
    ("Date de naissance", "date_naissance"),
]

_COLONNES_COMPTES = [
    Colonne("Type", 150),
    Colonne("IBAN", 290),
    Colonne("Solde", 130, "e"),
    Colonne("Statut", 90, "center"),
]


class VueTableauDeBord(Vue):
    """Informations personnelles, liste des comptes et accès aux opérations."""

    def __init__(
        self,
        parent: tk.Misc,
        informations: DonneesPersonnelles,
        comptes: list[LigneTableau],
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

        ttk.Label(
            self, text=f"Bonjour {informations.prenom}", style="Titre.TLabel"
        ).pack(anchor="w", pady=(0, 12))

        ttk.Label(self, text="Mes informations", style="Section.TLabel").pack(
            anchor="w"
        )
        bloc = ttk.Frame(self)
        bloc.pack(anchor="w", pady=(4, 12))
        for position, (libelle, attribut) in enumerate(_INFORMATIONS):
            ligne, colonne = divmod(position, 2)
            ttk.Label(bloc, text=f"{libelle} :").grid(
                row=ligne, column=colonne * 2, sticky="w", padx=(0, 6), pady=1
            )
            ttk.Label(bloc, text=getattr(informations, attribut)).grid(
                row=ligne, column=colonne * 2 + 1, sticky="w", padx=(0, 32), pady=1
            )

        ttk.Label(self, text="Mes comptes", style="Section.TLabel").pack(anchor="w")
        self._tableau = Tableau(self, _COLONNES_COMPTES, hauteur=6)
        self._tableau.remplir(comptes)
        self._tableau.sur_double_clic(on_detail)
        self._tableau.pack(fill="x", pady=(4, 8))

        ouverture = ttk.Frame(self)
        ouverture.pack(anchor="w")
        ttk.Label(ouverture, text="Ouvrir un nouveau compte :").pack(side="left")
        self._choix_type = ListeDeChoix(ouverture, types_de_compte, largeur=20)
        self._choix_type.pack(side="left", padx=8)
        ttk.Button(ouverture, text="Ouvrir", command=self._ouvrir).pack(side="left")

        self._placer_message()

        boutons = ttk.Frame(self)
        boutons.pack(anchor="w")
        for texte, action in [
            ("Voir le détail", self._detail),
            ("Opérations", on_operations),
            ("Historique", on_historique),
            ("Mon profil", on_profil),
            ("Se déconnecter", on_deconnexion),
        ]:
            ttk.Button(boutons, text=texte, command=action).pack(
                side="left", padx=(0, 8)
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
