-- KampusBank : jeu de données de test, à charger après sql/creation.sql :
--     mysql -u kampusbank -p kampusbank < sql/donnees_test.sql
-- 1 administrateur, 5 clients, 10 comptes, 35 transactions.
-- Les soldes sont cohérents avec les transactions : les données ont été produites
-- par les services de l'application (python -m kampusbank.demo).
-- Mots de passe : admin@kampusbank.fr / Admin2026 ; clients (…@demo.fr) / Demo2026.

INSERT INTO users (id, nom, prenom, email, telephone, adresse, date_naissance, mot_de_passe_hash, admin, echecs_connexion, bloque_jusqu_a) VALUES
    (1, 'Admin', 'KampusBank', 'admin@kampusbank.fr', '0100000000', '1 place de la Banque, 75002 Paris', '1990-01-01', '$2b$12$a5ubZNDwDA2A2/yVrhR4PeU6TDUpCxgSE.09CCjTi9TFAgoKNPywi', TRUE, 0, NULL),
    (2, 'Martin', 'Léa', 'lea.martin@demo.fr', '0611223344', '12 rue Oberkampf, Paris', '1999-03-14', '$2b$12$n6y9QEI1Tg2my8laBHSnd.Rghnmng1gjMoueFXxwF2mVvf8Z3eB9S', FALSE, 0, NULL),
    (3, 'Bernard', 'Hugo', 'hugo.bernard@demo.fr', '0622334455', '4 quai Perrache, Lyon', '1999-03-14', '$2b$12$nrHBynCcdB.hVM94/fuM2eQBBFm7b9rgFCufIOt9b78XewrYhYKt.', FALSE, 0, NULL),
    (4, 'Petit', 'Inès', 'ines.petit@demo.fr', '0633445566', '8 cours Julien, Marseille', '1999-03-14', '$2b$12$nb0TMPz8uwNMoZb5gfasZulybTAY1OzyiOd6y7XU/TF2T7ckDxzDy', FALSE, 0, NULL),
    (5, 'Robert', 'Yanis', 'yanis.robert@demo.fr', '0644556677', '2 rue Nationale, Lille', '1999-03-14', '$2b$12$XUI.vFEH5.PgSFchn3nAvuYKbwfkEjbBqnQFmL79OZ0mlHgOdKmqy', FALSE, 0, NULL),
    (6, 'Richard', 'Chloé', 'chloe.richard@demo.fr', '0655667788', '5 allée Jean Jaurès', '1999-03-14', '$2b$12$YSxtNQ1os1cvIuoSf0FCHuj3NkAjMXmYvVpW7vuNDbx/6VwgjZzDq', FALSE, 0, NULL);

INSERT INTO comptes_bancaires (id, proprietaire_id, iban, type, solde, statut, date_creation) VALUES
    (1, 2, 'FR76-KPBK-6114-6052-3829-0727-688', 'COURANT', '1522.00', 'ACTIF', '2026-10-25 14:27:53.180867'),
    (2, 2, 'FR76-KPBK-7281-7068-9876-9259-438', 'LIVRET_A', '2732.00', 'ACTIF', '2026-10-25 20:27:53.180867'),
    (3, 3, 'FR76-KPBK-7632-6750-1713-8472-707', 'COURANT', '1532.00', 'ACTIF', '2026-10-30 16:27:53.180867'),
    (4, 3, 'FR76-KPBK-9177-8120-7811-9535-598', 'LIVRET_A', '2063.00', 'ACTIF', '2026-10-30 21:27:53.180867'),
    (5, 4, 'FR76-KPBK-3354-4324-6040-3137-073', 'COURANT', '1546.00', 'ACTIF', '2026-11-03 22:27:53.180867'),
    (6, 4, 'FR76-KPBK-5317-3695-0142-9489-302', 'PEL', '3068.00', 'ACTIF', '2026-11-04 08:27:53.180867'),
    (7, 5, 'FR76-KPBK-6865-1360-9129-6640-468', 'COURANT', '1624.00', 'ACTIF', '2026-11-08 04:27:53.180867'),
    (8, 5, 'FR76-KPBK-2063-3175-4768-7071-653', 'LIVRET_A', '2505.00', 'ACTIF', '2026-11-08 11:27:53.180867'),
    (9, 6, 'FR76-KPBK-0328-9090-5544-3285-491', 'COURANT', '1620.00', 'ACTIF', '2026-11-13 19:27:53.180867'),
    (10, 6, 'FR76-KPBK-4052-5915-1028-6288-673', 'PEL', '2781.00', 'ACTIF', '2026-11-14 15:27:53.180867');

INSERT INTO transactions (id, compte_source_id, compte_destinataire_id, type, montant, libelle, `date`) VALUES
    (1, NULL, 1, 'DEPOT', '1850.00', 'Salaire', '2026-10-26 08:27:53.180867'),
    (2, NULL, 2, 'DEPOT', '2565.00', 'Épargne', '2026-10-26 22:27:53.180867'),
    (3, 1, NULL, 'RETRAIT', '170.00', 'Distributeur', '2026-10-27 10:27:53.180867'),
    (4, 1, 2, 'VIREMENT_EMIS', '167.00', 'Mise de côté', '2026-10-28 06:27:53.180867'),
    (5, 1, 2, 'VIREMENT_RECU', '167.00', 'Mise de côté', '2026-10-28 23:27:53.180867'),
    (6, NULL, 1, 'DEPOT', '60.00', 'Remboursement', '2026-10-29 08:27:53.180867'),
    (7, 1, NULL, 'RETRAIT', '51.00', 'Courses', '2026-10-29 23:27:53.180867'),
    (8, NULL, 3, 'DEPOT', '1850.00', 'Salaire', '2026-10-31 02:27:53.180867'),
    (9, NULL, 4, 'DEPOT', '1825.00', 'Épargne', '2026-10-31 08:27:53.180867'),
    (10, 3, NULL, 'RETRAIT', '101.00', 'Distributeur', '2026-10-31 21:27:53.180867'),
    (11, 3, 4, 'VIREMENT_EMIS', '238.00', 'Mise de côté', '2026-11-01 10:27:53.180867'),
    (12, 3, 4, 'VIREMENT_RECU', '238.00', 'Mise de côté', '2026-11-02 03:27:53.180867'),
    (13, NULL, 3, 'DEPOT', '89.00', 'Remboursement', '2026-11-02 13:27:53.180867'),
    (14, 3, NULL, 'RETRAIT', '68.00', 'Courses', '2026-11-02 22:27:53.180867'),
    (15, NULL, 5, 'DEPOT', '1850.00', 'Salaire', '2026-11-04 13:27:53.180867'),
    (16, NULL, 6, 'DEPOT', '2774.00', 'Épargne', '2026-11-04 23:27:53.180867'),
    (17, 5, NULL, 'RETRAIT', '91.00', 'Distributeur', '2026-11-05 08:27:53.180867'),
    (18, 5, 6, 'VIREMENT_EMIS', '294.00', 'Mise de côté', '2026-11-05 17:27:53.180867'),
    (19, 5, 6, 'VIREMENT_RECU', '294.00', 'Mise de côté', '2026-11-06 06:27:53.180867'),
    (20, NULL, 5, 'DEPOT', '120.00', 'Remboursement', '2026-11-06 21:27:53.180867'),
    (21, 5, NULL, 'RETRAIT', '39.00', 'Courses', '2026-11-07 07:27:53.180867'),
    (22, NULL, 7, 'DEPOT', '1850.00', 'Salaire', '2026-11-08 20:27:53.180867'),
    (23, NULL, 8, 'DEPOT', '2308.00', 'Épargne', '2026-11-09 10:27:53.180867'),
    (24, 7, NULL, 'RETRAIT', '110.00', 'Distributeur', '2026-11-10 06:27:53.180867'),
    (25, 7, 8, 'VIREMENT_EMIS', '197.00', 'Mise de côté', '2026-11-11 00:27:53.180867'),
    (26, 7, 8, 'VIREMENT_RECU', '197.00', 'Mise de côté', '2026-11-11 20:27:53.180867'),
    (27, NULL, 7, 'DEPOT', '120.00', 'Remboursement', '2026-11-12 01:27:53.180867'),
    (28, 7, NULL, 'RETRAIT', '39.00', 'Courses', '2026-11-12 16:27:53.180867'),
    (29, NULL, 9, 'DEPOT', '1850.00', 'Salaire', '2026-11-15 05:27:53.180867'),
    (30, NULL, 10, 'DEPOT', '2681.00', 'Épargne', '2026-11-16 01:27:53.180867'),
    (31, 9, NULL, 'RETRAIT', '104.00', 'Distributeur', '2026-11-16 14:27:53.180867'),
    (32, 9, 10, 'VIREMENT_EMIS', '100.00', 'Mise de côté', '2026-11-16 23:27:53.180867'),
    (33, 9, 10, 'VIREMENT_RECU', '100.00', 'Mise de côté', '2026-11-17 04:27:53.180867'),
    (34, NULL, 9, 'DEPOT', '48.00', 'Remboursement', '2026-11-17 17:27:53.180867'),
    (35, 9, NULL, 'RETRAIT', '74.00', 'Courses', '2026-11-18 05:27:53.180867');

UPDATE compteurs SET valeur = 6 WHERE entite = 'utilisateurs';
UPDATE compteurs SET valeur = 10 WHERE entite = 'comptes';
UPDATE compteurs SET valeur = 35 WHERE entite = 'transactions';
