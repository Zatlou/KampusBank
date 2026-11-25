-- KampusBank : préparation du serveur MySQL, à exécuter une seule fois
-- avec un compte administrateur MySQL :
--     mysql -u root -p < sql/installation.sql
--
-- Crée la base de l'application et un utilisateur qui n'a de droits que sur
-- elle (et sur les bases de test kampusbank_test_..., créées puis supprimées
-- par pytest). Ce mot de passe est celui d'un environnement de développement
-- local : en production, il ne serait pas écrit dans un fichier versionné.

CREATE DATABASE IF NOT EXISTS kampusbank
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'kampusbank'@'localhost' IDENTIFIED BY 'kampusbank';
CREATE USER IF NOT EXISTS 'kampusbank'@'127.0.0.1' IDENTIFIED BY 'kampusbank';

GRANT ALL PRIVILEGES ON kampusbank.* TO 'kampusbank'@'localhost';
GRANT ALL PRIVILEGES ON kampusbank.* TO 'kampusbank'@'127.0.0.1';
GRANT ALL PRIVILEGES ON `kampusbank\_test\_%`.* TO 'kampusbank'@'localhost';
GRANT ALL PRIVILEGES ON `kampusbank\_test\_%`.* TO 'kampusbank'@'127.0.0.1';
