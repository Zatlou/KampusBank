"""Jeu de données de démonstration : « python -m kampusbank.demo ».

Toutes les données passent par les services : les règles de gestion
s'appliquent (mots de passe hachés, IBAN uniques, soldes jamais négatifs).
Les clients déjà présents ne sont pas recréés.
"""

import os
import random
from datetime import datetime, timedelta
from functools import partial
from pathlib import Path

from kampusbank.assemblage import creer_depot
from kampusbank.config.parametres import charger_parametres
from kampusbank.domaine.iban import generer_iban
from kampusbank.service.authentification import ServiceAuthentification
from kampusbank.service.comptes import ServiceComptes
from kampusbank.service.formulaires import DonneesPersonnelles
from kampusbank.service.hachage import HacheurMotDePasse
from kampusbank.service.operations import ServiceOperations
from kampusbank.service.session import Session

MOT_DE_PASSE_DEMO = "Demo2026"

CLIENTS = [
    ("Martin", "Léa", "lea.martin@demo.fr", "0611223344", "12 rue Oberkampf, Paris"),
    ("Bernard", "Hugo", "hugo.bernard@demo.fr", "0622334455", "4 quai Perrache, Lyon"),
    ("Petit", "Inès", "ines.petit@demo.fr", "0633445566", "8 cours Julien, Marseille"),
    ("Robert", "Yanis", "yanis.robert@demo.fr", "0644556677", "2 rue Nationale, Lille"),
    ("Richard", "Chloé", "chloe.richard@demo.fr", "0655667788", "5 allée Jean Jaurès"),
]


class _Horloge:
    """Fait avancer le temps entre deux opérations, sur les 30 derniers jours."""

    def __init__(self) -> None:
        self.maintenant = datetime.now() - timedelta(days=30)

    def __call__(self) -> datetime:
        self.maintenant += timedelta(hours=random.randint(5, 20))
        return self.maintenant


def main() -> None:
    """Ajoute les clients, comptes et opérations de démonstration."""
    chemin = Path(os.environ.get("KAMPUSBANK_CONFIG", "kampusbank.toml"))
    parametres = charger_parametres(chemin)
    depot = creer_depot(parametres.persistance)
    session = Session()
    horloge = _Horloge()
    auth = ServiceAuthentification(
        depot,
        HacheurMotDePasse(parametres.securite.cout_bcrypt),
        session,
        echecs_max=parametres.securite.echecs_max,
        duree_blocage=timedelta(minutes=parametres.securite.duree_blocage_minutes),
        horloge=horloge,
    )
    comptes = ServiceComptes(
        depot, session, partial(generer_iban, random.Random()), horloge
    )
    operations = ServiceOperations(
        depot,
        session,
        parametres.operations.montant_minimum,
        parametres.operations.retrait_maximum,
        horloge,
    )

    crees = 0
    for nom, prenom, email, telephone, adresse in CLIENTS:
        if depot.trouver_utilisateur_par_email(email) is not None:
            continue
        auth.inscrire(
            DonneesPersonnelles(nom, prenom, email, telephone, adresse, "14/03/1999"),
            MOT_DE_PASSE_DEMO,
        )
        auth.connecter(email, MOT_DE_PASSE_DEMO)
        courant = comptes.ouvrir("COURANT")
        epargne = comptes.ouvrir(random.choice(["LIVRET_A", "PEL"]))
        operations.deposer(courant.id, "1850", "Salaire")
        operations.deposer(epargne.id, str(random.randint(200, 3000)), "Épargne")
        operations.retirer(courant.id, str(random.randint(40, 200)), "Distributeur")
        operations.virer_entre_mes_comptes(
            courant.id, epargne.id, str(random.randint(50, 300)), "Mise de côté"
        )
        operations.deposer(courant.id, str(random.randint(20, 150)), "Remboursement")
        operations.retirer(courant.id, str(random.randint(20, 80)), "Courses")
        auth.deconnecter()
        crees += 1

    print(f"{crees} client(s) de démonstration ajouté(s) (mot de passe : Demo2026).")


if __name__ == "__main__":
    main()
