"""Écran des opérations : un onglet pour le dépôt, le retrait et le virement."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from kampusbank.ihm.vues.base import Vue
from kampusbank.ihm.vues.liste_de_choix import ListeDeChoix

ActionSimple = Callable[[int, str, str], None]
ActionVirement = Callable[[int, int, str, str], None]
ActionVirementIban = Callable[[int, str, str, str], None]


class VueOperations(Vue):
    """Saisie des opérations ; les montants sont transmis tels que tapés."""

    def __init__(
        self,
        parent: tk.Misc,
        comptes: list[tuple[int, str]],
        on_depot: ActionSimple,
        on_retrait: ActionSimple,
        on_virement: ActionVirement,
        on_virement_iban: ActionVirementIban,
        on_retour: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self._comptes = comptes
        self._saisies: list[tk.StringVar] = []

        self._entete("Opérations", "Dépôt, retrait ou virement : choisissez un onglet.")
        onglets = ttk.Notebook(self)
        onglets.pack(fill="x")
        onglets.add(self._onglet_simple(onglets, "Déposer", on_depot), text="Dépôt")
        onglets.add(self._onglet_simple(onglets, "Retirer", on_retrait), text="Retrait")
        onglets.add(
            self._onglet_virement(onglets, on_virement, on_virement_iban),
            text="Virement",
        )

        self._placer_message()
        ttk.Button(self, text="Retour", command=on_retour).pack(anchor="w")

    def vider_saisies(self) -> None:
        """Efface les montants et libellés après une opération réussie."""
        for variable in self._saisies:
            variable.set("")

    def _onglet_simple(
        self, parent: ttk.Notebook, verbe: str, action: ActionSimple
    ) -> ttk.Frame:
        onglet = ttk.Frame(parent, padding=20)
        compte = self._ligne_compte(onglet, 0, "Compte")
        montant = self._ligne_saisie(onglet, 1, "Montant (€)")
        libelle = self._ligne_saisie(onglet, 2, "Libellé (facultatif)")

        def valider() -> None:
            compte_id = self._exiger_compte(compte)
            if compte_id is not None:
                action(compte_id, montant.get(), libelle.get())

        ttk.Button(onglet, text=verbe, command=valider, style="Primaire.TButton").grid(
            row=3, column=1, sticky="w", pady=(12, 0)
        )
        return onglet

    def _onglet_virement(
        self,
        parent: ttk.Notebook,
        action: ActionVirement,
        action_iban: ActionVirementIban,
    ) -> ttk.Frame:
        onglet = ttk.Frame(parent, padding=20)
        source = self._ligne_compte(onglet, 0, "Depuis")

        vers_iban = tk.BooleanVar(onglet, value=False)
        ttk.Radiobutton(
            onglet, text="Vers un de mes comptes", variable=vers_iban, value=False
        ).grid(row=1, column=0, sticky="w", pady=4)
        destination = ListeDeChoix(onglet, self._comptes, largeur=48)
        destination.grid(row=1, column=1, sticky="w", pady=4)
        ttk.Radiobutton(
            onglet, text="Vers un IBAN (autre client)", variable=vers_iban, value=True
        ).grid(row=2, column=0, sticky="w", pady=4)
        iban = self._champ(onglet, 2)

        montant = self._ligne_saisie(onglet, 3, "Montant (€)")
        libelle = self._ligne_saisie(onglet, 4, "Libellé (facultatif)")

        def valider() -> None:
            source_id = self._exiger_compte(source)
            if source_id is None:
                return
            if vers_iban.get():
                action_iban(source_id, iban.get(), montant.get(), libelle.get())
                return
            destination_id = self._exiger_compte(destination)
            if destination_id is not None:
                action(source_id, destination_id, montant.get(), libelle.get())

        ttk.Button(
            onglet, text="Virer", command=valider, style="Primaire.TButton"
        ).grid(row=5, column=1, sticky="w", pady=(12, 0))
        return onglet

    def _ligne_compte(
        self, parent: ttk.Frame, ligne: int, libelle: str
    ) -> ListeDeChoix[int]:
        ttk.Label(parent, text=libelle, style="Doux.TLabel").grid(
            row=ligne, column=0, sticky="w", padx=(0, 16), pady=5
        )
        choix = ListeDeChoix(parent, self._comptes, largeur=48)
        choix.grid(row=ligne, column=1, sticky="w", pady=4)
        return choix

    def _ligne_saisie(
        self, parent: ttk.Frame, ligne: int, libelle: str
    ) -> tk.StringVar:
        ttk.Label(parent, text=libelle, style="Doux.TLabel").grid(
            row=ligne, column=0, sticky="w", padx=(0, 16), pady=5
        )
        return self._champ(parent, ligne)

    def _champ(self, parent: ttk.Frame, ligne: int) -> tk.StringVar:
        variable = tk.StringVar(parent)
        ttk.Entry(parent, textvariable=variable, width=50).grid(
            row=ligne, column=1, sticky="w", pady=4
        )
        self._saisies.append(variable)
        return variable

    def _exiger_compte(self, choix: ListeDeChoix[int]) -> int | None:
        compte_id = choix.valeur()
        if compte_id is None:
            self.afficher_erreur("Ouvrez d'abord un compte depuis le tableau de bord.")
        return compte_id
