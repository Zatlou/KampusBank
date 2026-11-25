# Diagramme de classes UML

Le diagramme est découpé par couche pour rester lisible. Les attributs privés
sont préfixés par `-`, les éléments publics par `+`. Les propriétés en lecture
seule (`@property`) apparaissent comme des méthodes sans paramètre.

## 1. Vue d'ensemble des couches

```mermaid
flowchart TB
    subgraph ihm["ihm (Tkinter, MVC)"]
        V["Vues"]
        C["Contrôleurs"]
        R["Routeur"]
    end
    subgraph service["service"]
        S["Services + Session"]
    end
    subgraph persistance["persistance"]
        D["Depot (abstrait)"]
        DJ["DepotJson"]
        DM["DepotMySQL"]
    end
    subgraph domaine["domaine"]
        M["User, CompteBancaire, Transaction,<br/>validation, exceptions"]
    end
    subgraph config["config"]
        P["Parametres (kampusbank.toml)"]
    end
    A["assemblage.py"]

    V -->|"saisies"| C
    C -->|"appelle"| S
    C --> R
    S --> D
    S --> M
    DJ -.->|"implémente"| D
    DM -.->|"implémente"| D
    D --> M
    A -->|"crée et relie"| C
    A --> S
    A --> DJ
    A --> DM
    A --> P
```

## 2. Domaine

```mermaid
classDiagram
    direction TB

    class User {
        -int _id
        -str _nom
        -str _prenom
        -str _email
        -str _telephone
        -str _adresse
        -date _date_naissance
        -str _mot_de_passe_hash
        -bool _admin
        -int _echecs_connexion
        -datetime _bloque_jusqu_a
        +modifier_informations(nom, prenom, email, telephone, adresse, date_naissance)
        +fin_de_blocage(maintenant) datetime
        +enregistrer_echec_connexion(maintenant, echecs_max, duree_blocage)
        +reinitialiser_echecs_connexion()
        +nom_complet() str
    }

    class CompteBancaire {
        <<abstract>>
        +str CODE$
        +str LIBELLE$
        -int _id
        -int _proprietaire_id
        -str _iban
        -Decimal _solde
        -StatutCompte _statut
        -datetime _date_creation
        +plafond()* Decimal
        +verifier_credit(montant)
        +verifier_debit(montant)
        +verifier_retrait(montant)
        +crediter(montant)
        +debiter(montant)
        +retirer(montant)
        +verifier_suppression()
        +bloquer()
        +debloquer()
        +type() str
    }

    class CompteCourant {
        +CODE = "COURANT"
        +plafond() None
    }
    class LivretA {
        +CODE = "LIVRET_A"
        +plafond() 22 950,00
    }
    class PEL {
        +CODE = "PEL"
        +plafond() 61 200,00
        +verifier_retrait(montant)
    }

    class StatutCompte {
        <<enumeration>>
        ACTIF
        BLOQUE
    }

    class Transaction {
        <<dataclass frozen>>
        +int id
        +int compte_source_id
        +int compte_destinataire_id
        +TypeTransaction type
        +Decimal montant
        +datetime date
        +str libelle
        +est_credit() bool
        +compte_concerne_id() int
    }

    class TypeTransaction {
        <<enumeration>>
        DEPOT
        RETRAIT
        VIREMENT_EMIS
        VIREMENT_RECU
        ANNULATION
    }

    class FiltreHistorique {
        <<dataclass frozen>>
        +frozenset comptes_ids
        +TypeTransaction type
        +date du
        +date au
        +accepte(transaction) bool
    }

    class validation {
        <<module>>
        +valider_email(email) str
        +valider_telephone(telephone) str
        +valider_mot_de_passe(mot_de_passe) str
        +lire_montant(texte) Decimal
        +valider_montant(montant) Decimal
        +lire_date(texte) date
    }

    CompteBancaire <|-- CompteCourant
    CompteBancaire <|-- LivretA
    CompteBancaire <|-- PEL
    CompteBancaire --> StatutCompte
    User "1" <-- "0..*" CompteBancaire : proprietaire_id
    Transaction --> TypeTransaction
    Transaction "0..*" --> "0..1" CompteBancaire : source
    Transaction "0..*" --> "0..1" CompteBancaire : destinataire
    FiltreHistorique ..> Transaction : filtre
    User ..> validation : utilise
    CompteBancaire ..> validation : utilise
    Transaction ..> validation : utilise
```

## 3. Exceptions métier

```mermaid
classDiagram
    direction LR
    Exception <|-- KampusBankError
    KampusBankError <|-- DonneeInvalideError
    DonneeInvalideError <|-- EmailInvalideError
    DonneeInvalideError <|-- TelephoneInvalideError
    DonneeInvalideError <|-- MotDePasseInvalideError
    DonneeInvalideError <|-- MontantInvalideError
    DonneeInvalideError <|-- DateInvalideError
    DonneeInvalideError <|-- IbanInvalideError
    DonneeInvalideError <|-- ChampObligatoireError
    KampusBankError <|-- EmailDejaUtiliseError
    KampusBankError <|-- IdentifiantsInvalidesError
    KampusBankError <|-- UtilisateurBloqueError
    KampusBankError <|-- NonConnecteError
    KampusBankError <|-- AccesRefuseError
    KampusBankError <|-- SoldeInsuffisantError
    KampusBankError <|-- CompteBloqueError
    KampusBankError <|-- CompteNonVideError
    KampusBankError <|-- LimiteOperationError
    KampusBankError <|-- PlafondDepasseError
    KampusBankError <|-- RetraitInterditError
    KampusBankError <|-- VirementInvalideError
    KampusBankError <|-- AnnulationImpossibleError
    KampusBankError <|-- CompteIntrouvableError
    KampusBankError <|-- ClientIntrouvableError
    KampusBankError <|-- SuppressionClientImpossibleError
    KampusBankError <|-- TypeCompteInconnuError
```

## 4. Services et persistance

```mermaid
classDiagram
    direction TB

    class Session {
        -User _utilisateur
        +ouvrir(utilisateur)
        +fermer()
        +exiger_connexion() User
        +exiger_admin() User
    }

    class HacheurMotDePasse {
        -int _cout
        +hacher(mot_de_passe) str
        +verifier(mot_de_passe, empreinte) bool
    }

    class ServiceAuthentification {
        +inscrire(donnees, mot_de_passe) User
        +connecter(email, mot_de_passe) User
        +deconnecter()
        +creer_administrateur_initial(donnees, mot_de_passe)
    }
    class ServiceProfil {
        +consulter() User
        +modifier(donnees) User
    }
    class ServiceComptes {
        +types_disponibles() list
        +lister() list
        +solde_total() Decimal
        +consulter(compte_id) CompteBancaire
        +ouvrir(code_type) CompteBancaire
        +supprimer(compte_id)
    }
    class ServiceOperations {
        +deposer(compte_id, montant, libelle) Transaction
        +retirer(compte_id, montant, libelle) Transaction
        +virer_entre_mes_comptes(source_id, destination_id, montant, libelle) Transaction
        +virer_vers_iban(source_id, iban, montant, libelle) Transaction
        +historique(compte_id, type_operation, du, au) list
    }
    class ServiceAdministration {
        +lister_clients() list
        +rechercher_clients(nom, email, numero_compte) list
        +modifier_client(client_id, donnees) User
        +supprimer_client(client_id)
        +basculer_blocage(compte_id) CompteBancaire
        +historique_compte(compte_id) list
        +annuler_derniere_operation(compte_id) Transaction
        +statistiques() Statistiques
    }

    class Depot {
        <<abstract>>
        +prochain_id_utilisateur()* int
        +enregistrer_utilisateur(utilisateur)*
        +trouver_utilisateur_par_email(email)* User
        +prochain_id_compte()* int
        +enregistrer_compte(compte)*
        +trouver_compte_par_iban(iban)* CompteBancaire
        +enregistrer_operation(comptes, transactions)*
        +lister_transactions(filtre)* list
        +...()
    }
    class DepotJson {
        -Path _fichier
        -dict _donnees
        -_modifier(modification)
        -_ecrire(donnees)
    }
    class DepotMySQL {
        -Connection _connexion
        -_transaction() Cursor
        +fermer()
    }

    Depot <|-- DepotJson
    Depot <|-- DepotMySQL
    ServiceAuthentification --> Depot
    ServiceAuthentification --> HacheurMotDePasse
    ServiceAuthentification --> Session
    ServiceProfil --> Depot
    ServiceProfil --> Session
    ServiceComptes --> Depot
    ServiceComptes --> Session
    ServiceOperations --> Depot
    ServiceOperations --> Session
    ServiceAdministration --> Depot
    ServiceAdministration --> Session
```

## 5. Interface (MVC)

Vue simplifiée : toutes les vues héritent de `Vue` (un `ttk.Frame`), et chaque
contrôleur ne parle qu'à son service.

```mermaid
flowchart TB
    subgraph vues["Vues : héritent de Vue (ttk.Frame), affichent et transmettent"]
        V1["VueConnexion<br/>VueInscription"]
        V2["VueTableauDeBord<br/>VueProfil · VueDetailCompte"]
        V3["VueOperations<br/>VueHistorique"]
        V4["VueAccueilAdmin · VueFicheClient<br/>VueComptesAdmin · VueHistoriqueCompte"]
    end
    subgraph controleurs["Contrôleurs : appellent les services, affichent le résultat"]
        C1["ControleurAuthentification"]
        C2["ControleurClient"]
        C3["ControleurOperations"]
        C4["ControleurAdministration"]
    end
    subgraph services["Services (modèle)"]
        S1["ServiceAuthentification"]
        S2["ServiceProfil<br/>ServiceComptes"]
        S3["ServiceOperations"]
        S4["ServiceAdministration"]
    end
    F["FenetrePrincipale<br/>bandeau + écran affiché"]
    R["Routeur<br/>écran → méthode qui l'affiche"]

    V1 -->|"on_connexion(email, mot_de_passe)"| C1
    V2 -->|"on_ouvrir_compte(code)"| C2
    V3 -->|"on_depot(compte, montant, libellé)"| C3
    V4 -->|"on_annuler(compte)"| C4
    C1 --> S1
    C2 --> S2
    C3 --> S3
    C4 --> S4
    controleurs -->|"afficher(vue)"| F
    controleurs -->|"aller_a(Ecran)"| R
```
