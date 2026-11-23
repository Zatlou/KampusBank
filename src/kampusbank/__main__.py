"""Point d'entrée : « python -m kampusbank » ou la commande « kampusbank »."""

import os
from pathlib import Path

from kampusbank.assemblage import construire_application


def main() -> None:
    """Lance l'application avec kampusbank.toml (ou le fichier de KAMPUSBANK_CONFIG)."""
    chemin = Path(os.environ.get("KAMPUSBANK_CONFIG", "kampusbank.toml"))
    construire_application(chemin).lancer()


if __name__ == "__main__":
    main()
