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

## Données de démonstration

```bash
python -m kampusbank.demo
```

Ajoute 5 clients, 10 comptes et 35 opérations, en passant par les services (les
règles de gestion s'appliquent). Mot de passe de tous les clients : `Demo2026`
(par exemple `lea.martin@demo.fr`). Relancer la commande n'ajoute rien de plus.

## Persistance MySQL (facultative)

1. Créer la base et son utilisateur, une seule fois, avec un compte administrateur MySQL :
   ```bash
   mysql -u root -p < sql/installation.sql
   ```
2. Créer les tables, puis, si on le souhaite, charger le jeu de données de test
   (mot de passe de l'utilisateur MySQL : `kampusbank`) :
   ```bash
   mysql -u kampusbank -p kampusbank < sql/creation.sql
   mysql -u kampusbank -p kampusbank < sql/donnees_test.sql
   ```
3. Dans `kampusbank.toml`, remplacer `type = "json"` par `type = "mysql"`, puis lancer
   `kampusbank` comme d'habitude.

Les tests du dépôt MySQL sont ignorés par défaut ; pour les lancer :

```bash
KAMPUSBANK_TEST_MYSQL=1 pytest
```

## Documentation

- `docs/dossier_conception.md` : dossier de conception (exigences EC1 à EC10)
- `docs/diagramme_classes.md` : diagramme de classes UML
- `docs/mcd_mld.md` : MCD, MLD et modèle physique de la base

## Configuration

Tous les paramètres variables sont dans `kampusbank.toml` : type de persistance,
fichier de données, administrateur initial, seuils de blocage des connexions,
montant minimum d'une opération et maximum d'un retrait.

## Organisation du code

```
src/kampusbank/
├── domaine/       modèle métier, règles de gestion, exceptions
├── service/       opérations de l'application et contrôle d'accès
├── persistance/   enregistrement des données (JSON, MySQL)
├── ihm/           vues et contrôleurs Tkinter
└── config/        lecture de kampusbank.toml
tests/             tests pytest
sql/               scripts MySQL (installation, tables, données de test)
docs/              dossier de conception, UML, MCD/MLD
```
