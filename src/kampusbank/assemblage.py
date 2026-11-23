"""Module d'assemblage : crée tous les objets et les relie entre eux.

C'est le seul endroit qui choisit les implémentations concrètes (dépôt JSON,
bcrypt, horloge système). Chaque objet reçoit ses dépendances par son
constructeur : on peut donc en substituer d'autres dans les tests.
"""

from datetime import datetime, timedelta
from pathlib import Path

from kampusbank.config.parametres import ParametresPersistance, charger_parametres
from kampusbank.ihm.controleurs.administration import ControleurAdministration
from kampusbank.ihm.controleurs.authentification import ControleurAuthentification
from kampusbank.ihm.controleurs.client import ControleurClient
from kampusbank.ihm.fenetre import FenetrePrincipale
from kampusbank.ihm.routeur import Ecran, Routeur
from kampusbank.persistance.depot import Depot
from kampusbank.persistance.depot_json import DepotJson
from kampusbank.service.administration import ServiceAdministration
from kampusbank.service.authentification import ServiceAuthentification
from kampusbank.service.formulaires import DonneesPersonnelles
from kampusbank.service.hachage import HacheurMotDePasse
from kampusbank.service.profil import ServiceProfil
from kampusbank.service.session import Session


def creer_depot(parametres: ParametresPersistance) -> Depot:
    """Choisit l'implémentation de la persistance indiquée dans la configuration."""
    if parametres.type == "json":
        return DepotJson(parametres.fichier)
    raise ValueError(f"Type de persistance inconnu : « {parametres.type} ».")


def construire_application(chemin_configuration: Path) -> FenetrePrincipale:
    """Construit l'application complète et affiche l'écran de connexion."""
    parametres = charger_parametres(chemin_configuration)

    depot = creer_depot(parametres.persistance)
    session = Session()
    authentification = ServiceAuthentification(
        depot,
        HacheurMotDePasse(parametres.securite.cout_bcrypt),
        session,
        echecs_max=parametres.securite.echecs_max,
        duree_blocage=timedelta(minutes=parametres.securite.duree_blocage_minutes),
        horloge=datetime.now,
    )
    profil = ServiceProfil(depot, session)
    administration = ServiceAdministration(depot, session)

    admin = parametres.administrateur
    authentification.creer_administrateur_initial(
        DonneesPersonnelles(
            nom=admin.nom,
            prenom=admin.prenom,
            email=admin.email,
            telephone=admin.telephone,
            adresse=admin.adresse,
            date_naissance=admin.date_naissance,
        ),
        admin.mot_de_passe,
    )

    fenetre = FenetrePrincipale("KampusBank")
    routeur = Routeur()
    controleur_authentification = ControleurAuthentification(
        fenetre, routeur, authentification
    )
    controleur_client = ControleurClient(fenetre, routeur, profil, authentification)
    controleur_admin = ControleurAdministration(
        fenetre, routeur, administration, authentification
    )

    routeur.enregistrer(Ecran.CONNEXION, controleur_authentification.afficher_connexion)
    routeur.enregistrer(
        Ecran.INSCRIPTION, controleur_authentification.afficher_inscription
    )
    routeur.enregistrer(
        Ecran.TABLEAU_DE_BORD, controleur_client.afficher_tableau_de_bord
    )
    routeur.enregistrer(Ecran.PROFIL, controleur_client.afficher_profil)
    routeur.enregistrer(Ecran.ACCUEIL_ADMIN, controleur_admin.afficher_accueil)

    routeur.aller_a(Ecran.CONNEXION)
    return fenetre
