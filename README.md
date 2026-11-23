# KampusBank

Application de bureau de gestion bancaire pour une banque fictive, KampusBank.
Les clients gèrent leurs comptes et leurs opérations ; les administrateurs supervisent
l'ensemble du système.

Python 3.12+, interface Tkinter (MVC), persistance JSON (MySQL en option), tests pytest.

## Prérequis

- Python 3.12 ou plus récent, avec Tkinter
- MySQL 8 (uniquement pour la persistance MySQL, facultative)

## Installation

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Tests et vérifications

```bash
pytest
mypy
ruff check .
```

## Lancement

Depuis la racine du projet, environnement virtuel activé :

```bash
kampusbank
```

(équivalent : `python -m kampusbank`). Un autre fichier de configuration peut être
indiqué avec la variable d'environnement `KAMPUSBANK_CONFIG`.

Au premier lancement, l'administrateur décrit dans `kampusbank.toml` est créé
(par défaut `admin@kampusbank.fr` / `Admin2026`). Les clients créent leur compte
depuis l'écran de connexion.

## Configuration

Tous les paramètres variables sont dans `kampusbank.toml` : type de persistance,
fichier de données, administrateur initial, seuils de blocage des connexions.

## Organisation du code

```
src/kampusbank/
├── domaine/       modèle métier, règles de gestion, exceptions
├── service/       opérations de l'application et contrôle d'accès
├── persistance/   enregistrement des données (JSON, MySQL)
├── ihm/           vues et contrôleurs Tkinter
└── config/        lecture de kampusbank.toml
tests/             tests pytest
```
