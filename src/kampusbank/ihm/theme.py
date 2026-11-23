"""Thème graphique : couleurs, polices et styles ttk de toute l'application.

Les vues ne choisissent jamais une couleur elles-mêmes : elles utilisent les
styles nommés ici (« Primaire.TButton », « Titre.TLabel »…). Changer l'allure de
l'application se fait dans ce seul fichier.
"""

import tkinter as tk
from tkinter import ttk

PRIMAIRE = "#1E3A8A"
PRIMAIRE_SURVOL = "#1D4ED8"
PRIMAIRE_CLAIR = "#DBEAFE"
FOND = "#FFFFFF"
FOND_DOUX = "#F3F4F6"
LIGNE_ALTERNEE = "#F9FAFB"
BORDURE = "#D1D5DB"
TEXTE = "#111827"
TEXTE_DOUX = "#6B7280"
SUCCES = "#15803D"
ERREUR = "#B91C1C"
DANGER_FOND = "#FEE2E2"
POLICE = "Helvetica Neue"


def appliquer_theme(racine: tk.Tk) -> None:
    """Configure les styles ttk de la fenêtre."""
    racine.configure(background=FOND)
    style = ttk.Style(racine)
    style.theme_use("clam")

    style.configure(".", background=FOND, foreground=TEXTE, font=(POLICE, 13))
    style.configure("TFrame", background=FOND)
    style.configure("TLabel", background=FOND, foreground=TEXTE)
    style.configure("Titre.TLabel", font=(POLICE, 24, "bold"), foreground=PRIMAIRE)
    style.configure("Section.TLabel", font=(POLICE, 15, "bold"))
    style.configure("Doux.TLabel", foreground=TEXTE_DOUX)
    style.configure("Etiquette.TLabel", foreground=TEXTE_DOUX, font=(POLICE, 11))
    style.configure("Chiffre.TLabel", font=(POLICE, 22, "bold"), foreground=PRIMAIRE)
    style.configure("Erreur.TLabel", foreground=ERREUR, font=(POLICE, 13, "bold"))
    style.configure("Succes.TLabel", foreground=SUCCES, font=(POLICE, 13, "bold"))

    style.configure("Bandeau.TFrame", background=PRIMAIRE)
    style.configure(
        "Bandeau.TLabel",
        background=PRIMAIRE,
        foreground="white",
        font=(POLICE, 20, "bold"),
    )
    style.configure(
        "BandeauDoux.TLabel", background=PRIMAIRE, foreground=PRIMAIRE_CLAIR
    )
    style.configure("Tuile.TFrame", background=FOND_DOUX)
    style.configure("Tuile.TLabel", background=FOND_DOUX, foreground=TEXTE_DOUX)
    style.configure(
        "TuileChiffre.TLabel",
        background=FOND_DOUX,
        foreground=PRIMAIRE,
        font=(POLICE, 20, "bold"),
    )

    style.configure(
        "TButton",
        padding=(14, 7),
        background=FOND_DOUX,
        foreground=TEXTE,
        bordercolor=BORDURE,
        lightcolor=FOND_DOUX,
        darkcolor=FOND_DOUX,
        focuscolor=FOND_DOUX,
    )
    style.map("TButton", background=[("active", BORDURE)])
    style.configure(
        "Primaire.TButton",
        background=PRIMAIRE,
        foreground="white",
        bordercolor=PRIMAIRE,
        lightcolor=PRIMAIRE,
        darkcolor=PRIMAIRE,
        focuscolor=PRIMAIRE,
        font=(POLICE, 13, "bold"),
    )
    style.map(
        "Primaire.TButton",
        background=[("active", PRIMAIRE_SURVOL)],
        foreground=[("active", "white")],
    )
    style.configure(
        "Danger.TButton",
        background=FOND,
        foreground=ERREUR,
        bordercolor=ERREUR,
        lightcolor=FOND,
        darkcolor=FOND,
        focuscolor=FOND,
    )
    style.map("Danger.TButton", background=[("active", DANGER_FOND)])

    style.configure(
        "TEntry",
        padding=6,
        fieldbackground=FOND,
        bordercolor=BORDURE,
        lightcolor=BORDURE,
    )
    style.map(
        "TEntry", bordercolor=[("focus", PRIMAIRE)], lightcolor=[("focus", PRIMAIRE)]
    )
    style.configure(
        "TCombobox",
        padding=5,
        fieldbackground=FOND,
        background=FOND_DOUX,
        bordercolor=BORDURE,
        arrowcolor=PRIMAIRE,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", FOND)],
        selectbackground=[("readonly", FOND)],
        selectforeground=[("readonly", TEXTE)],
    )
    racine.option_add("*TCombobox*Listbox.background", FOND)
    racine.option_add("*TCombobox*Listbox.selectBackground", PRIMAIRE_CLAIR)
    racine.option_add("*TCombobox*Listbox.selectForeground", TEXTE)
    style.configure("TRadiobutton", background=FOND)

    style.configure(
        "Treeview",
        background=FOND,
        fieldbackground=FOND,
        foreground=TEXTE,
        rowheight=30,
        bordercolor=BORDURE,
    )
    style.map(
        "Treeview",
        background=[("selected", PRIMAIRE_CLAIR)],
        foreground=[("selected", TEXTE)],
    )
    style.configure(
        "Treeview.Heading",
        background=FOND_DOUX,
        foreground=TEXTE_DOUX,
        font=(POLICE, 12, "bold"),
        padding=(8, 6),
        bordercolor=BORDURE,
    )
    style.map("Treeview.Heading", background=[("active", BORDURE)])

    style.configure("TNotebook", background=FOND, bordercolor=BORDURE)
    style.configure(
        "TNotebook.Tab",
        padding=(18, 8),
        background=FOND_DOUX,
        foreground=TEXTE_DOUX,
        bordercolor=BORDURE,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", FOND)],
        foreground=[("selected", PRIMAIRE)],
    )
