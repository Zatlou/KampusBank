from datetime import timedelta
from pathlib import Path

import pytest

from kampusbank.domaine.exceptions import (
    EmailDejaUtiliseError,
    IdentifiantsInvalidesError,
    MotDePasseInvalideError,
    UtilisateurBloqueError,
)
from kampusbank.persistance.depot_json import DepotJson
from kampusbank.service.authentification import ServiceAuthentification
from kampusbank.service.hachage import HacheurMotDePasse
from kampusbank.service.session import Session
from tests.fabriques import DUREE_BLOCAGE_MINUTES, ECHECS_MAX, HorlogeFactice
from tests.saisies import MOT_DE_PASSE_VALIDE, donnees_valides


class TestInscription:
    def test_inscription_cree_un_client(
        self, auth: ServiceAuthentification, depot: DepotJson
    ) -> None:
        cree = auth.inscrire(donnees_valides(), MOT_DE_PASSE_VALIDE)

        assert cree.admin is False
        assert [u.email for u in depot.lister_utilisateurs()] == ["alice@exemple.fr"]

    def test_rg1_mot_de_passe_hache_jamais_en_clair(
        self,
        auth: ServiceAuthentification,
        hacheur: HacheurMotDePasse,
        fichier_donnees: Path,
    ) -> None:
        cree = auth.inscrire(donnees_valides(), MOT_DE_PASSE_VALIDE)

        assert cree.mot_de_passe_hash != MOT_DE_PASSE_VALIDE
        assert cree.mot_de_passe_hash.startswith("$2b$")
        assert hacheur.verifier(MOT_DE_PASSE_VALIDE, cree.mot_de_passe_hash)
        assert MOT_DE_PASSE_VALIDE not in fichier_donnees.read_text(encoding="utf-8")

    def test_rg14_email_deja_utilise_meme_avec_majuscules(
        self, auth: ServiceAuthentification
    ) -> None:
        auth.inscrire(donnees_valides(), MOT_DE_PASSE_VALIDE)

        with pytest.raises(EmailDejaUtiliseError):
            auth.inscrire(
                donnees_valides(email="ALICE@exemple.fr"), MOT_DE_PASSE_VALIDE
            )

    def test_rg16_mot_de_passe_faible_aucun_compte_cree(
        self, auth: ServiceAuthentification, depot: DepotJson
    ) -> None:
        with pytest.raises(MotDePasseInvalideError):
            auth.inscrire(donnees_valides(), "faible")

        assert depot.lister_utilisateurs() == []

    def test_administrateur_initial_cree_une_seule_fois(
        self, auth: ServiceAuthentification, depot: DepotJson
    ) -> None:
        donnees_admin = donnees_valides(email="admin@kampusbank.fr")
        auth.creer_administrateur_initial(donnees_admin, MOT_DE_PASSE_VALIDE)
        auth.creer_administrateur_initial(donnees_admin, MOT_DE_PASSE_VALIDE)

        utilisateurs = depot.lister_utilisateurs()
        assert len(utilisateurs) == 1
        assert utilisateurs[0].admin is True


class TestConnexion:
    @pytest.fixture(autouse=True)
    def client_inscrit(self, auth: ServiceAuthentification) -> None:
        auth.inscrire(donnees_valides(), MOT_DE_PASSE_VALIDE)

    def test_connexion_reussie_ouvre_la_session(
        self, auth: ServiceAuthentification, session: Session
    ) -> None:
        connecte = auth.connecter(" Alice@Exemple.fr ", MOT_DE_PASSE_VALIDE)

        assert session.utilisateur is connecte

    def test_mauvais_mot_de_passe_refuse(self, auth: ServiceAuthentification) -> None:
        with pytest.raises(IdentifiantsInvalidesError):
            auth.connecter("alice@exemple.fr", "Mauvais123")

    def test_email_inconnu_meme_message_que_mauvais_mot_de_passe(
        self, auth: ServiceAuthentification
    ) -> None:
        with pytest.raises(IdentifiantsInvalidesError) as erreur_email:
            auth.connecter("inconnu@exemple.fr", MOT_DE_PASSE_VALIDE)
        with pytest.raises(IdentifiantsInvalidesError) as erreur_mot_de_passe:
            auth.connecter("alice@exemple.fr", "Mauvais123")

        assert str(erreur_email.value) == str(erreur_mot_de_passe.value)

    def test_deconnexion_ferme_la_session(
        self, auth: ServiceAuthentification, session: Session
    ) -> None:
        auth.connecter("alice@exemple.fr", MOT_DE_PASSE_VALIDE)
        auth.deconnecter()

        assert session.utilisateur is None


class TestRG3BlocageApresEchecs:
    @pytest.fixture(autouse=True)
    def client_inscrit(self, auth: ServiceAuthentification) -> None:
        auth.inscrire(donnees_valides(), MOT_DE_PASSE_VALIDE)

    def _echouer(self, auth: ServiceAuthentification, fois: int) -> None:
        for _ in range(fois):
            with pytest.raises(IdentifiantsInvalidesError):
                auth.connecter("alice@exemple.fr", "Mauvais123")

    def test_le_cinquieme_echec_bloque(self, auth: ServiceAuthentification) -> None:
        self._echouer(auth, ECHECS_MAX - 1)

        with pytest.raises(UtilisateurBloqueError):
            auth.connecter("alice@exemple.fr", "Mauvais123")

    def test_meme_le_bon_mot_de_passe_est_refuse_pendant_le_blocage(
        self, auth: ServiceAuthentification, horloge: HorlogeFactice
    ) -> None:
        self._echouer(auth, ECHECS_MAX - 1)
        with pytest.raises(UtilisateurBloqueError):
            auth.connecter("alice@exemple.fr", "Mauvais123")

        horloge.avancer(DUREE_BLOCAGE_MINUTES - 1)
        with pytest.raises(UtilisateurBloqueError):
            auth.connecter("alice@exemple.fr", MOT_DE_PASSE_VALIDE)

    def test_connexion_possible_apres_quinze_minutes(
        self, auth: ServiceAuthentification, horloge: HorlogeFactice
    ) -> None:
        self._echouer(auth, ECHECS_MAX - 1)
        with pytest.raises(UtilisateurBloqueError):
            auth.connecter("alice@exemple.fr", "Mauvais123")

        horloge.avancer(DUREE_BLOCAGE_MINUTES)

        assert (
            auth.connecter("alice@exemple.fr", MOT_DE_PASSE_VALIDE).email
            == "alice@exemple.fr"
        )

    def test_seuls_les_echecs_consecutifs_comptent(
        self, auth: ServiceAuthentification
    ) -> None:
        self._echouer(auth, ECHECS_MAX - 1)
        auth.connecter("alice@exemple.fr", MOT_DE_PASSE_VALIDE)

        self._echouer(auth, ECHECS_MAX - 1)

    def test_le_blocage_survit_a_un_redemarrage(
        self,
        auth: ServiceAuthentification,
        hacheur: HacheurMotDePasse,
        horloge: HorlogeFactice,
        fichier_donnees: Path,
    ) -> None:
        self._echouer(auth, ECHECS_MAX - 1)
        with pytest.raises(UtilisateurBloqueError):
            auth.connecter("alice@exemple.fr", "Mauvais123")

        apres_redemarrage = ServiceAuthentification(
            DepotJson(fichier_donnees),
            hacheur,
            Session(),
            echecs_max=ECHECS_MAX,
            duree_blocage=timedelta(minutes=DUREE_BLOCAGE_MINUTES),
            horloge=horloge,
        )
        with pytest.raises(UtilisateurBloqueError):
            apres_redemarrage.connecter("alice@exemple.fr", MOT_DE_PASSE_VALIDE)
