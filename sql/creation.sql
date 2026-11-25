-- KampusBank : création des tables (MLD), dans la base kampusbank :
--     mysql -u kampusbank -p kampusbank < sql/creation.sql
-- Attention : les tables existantes sont supprimées, avec leurs données.

DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS comptes_bancaires;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS compteurs;

-- Un utilisateur : client ou administrateur.
CREATE TABLE users (
    id                INT          NOT NULL,
    nom               VARCHAR(100) NOT NULL,
    prenom            VARCHAR(100) NOT NULL,
    email             VARCHAR(255) NOT NULL,
    telephone         CHAR(10)     NOT NULL,
    adresse           VARCHAR(255) NOT NULL DEFAULT '',
    date_naissance    DATE         NOT NULL,
    mot_de_passe_hash CHAR(60)     NOT NULL,
    admin             BOOLEAN      NOT NULL DEFAULT FALSE,
    echecs_connexion  INT          NOT NULL DEFAULT 0,
    bloque_jusqu_a    DATETIME(6)  NULL,
    CONSTRAINT pk_users PRIMARY KEY (id),
    CONSTRAINT uq_users_email UNIQUE (email)
) ENGINE = InnoDB;

-- Un compte appartient à un client (1:N). Le type reste un texte libre et non
-- une ENUM : ajouter un type de compte ne demande pas de modifier la table (EC2).
CREATE TABLE comptes_bancaires (
    id              INT           NOT NULL,
    proprietaire_id INT           NOT NULL,
    iban            CHAR(33)      NOT NULL,
    type            VARCHAR(20)   NOT NULL,
    solde           DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    statut          ENUM('ACTIF', 'BLOQUE') NOT NULL DEFAULT 'ACTIF',
    date_creation   DATETIME(6)   NOT NULL,
    CONSTRAINT pk_comptes PRIMARY KEY (id),
    CONSTRAINT uq_comptes_iban UNIQUE (iban),
    CONSTRAINT ck_solde_jamais_negatif CHECK (solde >= 0),
    CONSTRAINT fk_comptes_proprietaire FOREIGN KEY (proprietaire_id)
        REFERENCES users (id) ON DELETE CASCADE
) ENGINE = InnoDB;

-- Le journal des opérations. Les comptes source et destinataire ne sont pas des
-- clés étrangères : l'historique est conservé même après la suppression d'un
-- compte (RG6), comme sur un relevé bancaire.
CREATE TABLE transactions (
    id                     INT           NOT NULL,
    compte_source_id       INT           NULL,
    compte_destinataire_id INT           NULL,
    type                   ENUM('DEPOT', 'RETRAIT', 'VIREMENT_EMIS',
                                'VIREMENT_RECU', 'ANNULATION') NOT NULL,
    montant                DECIMAL(12,2) NOT NULL,
    libelle                VARCHAR(255)  NOT NULL DEFAULT '',
    `date`                 DATETIME(6)   NOT NULL,
    CONSTRAINT pk_transactions PRIMARY KEY (id),
    CONSTRAINT ck_montant_positif CHECK (montant > 0),
    CONSTRAINT ck_au_moins_un_compte
        CHECK (compte_source_id IS NOT NULL OR compte_destinataire_id IS NOT NULL),
    INDEX ix_transactions_source (compte_source_id),
    INDEX ix_transactions_destinataire (compte_destinataire_id)
) ENGINE = InnoDB;

-- Prochain identifiant de chaque table : un identifiant n'est jamais réattribué,
-- même après une suppression.
CREATE TABLE compteurs (
    entite VARCHAR(20) NOT NULL,
    valeur INT         NOT NULL,
    CONSTRAINT pk_compteurs PRIMARY KEY (entite)
) ENGINE = InnoDB;

INSERT INTO compteurs (entite, valeur) VALUES
    ('utilisateurs', 0),
    ('comptes', 0),
    ('transactions', 0);
