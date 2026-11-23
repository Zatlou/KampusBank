"""Accès d'un client à ses propres comptes uniquement."""

from kampusbank.domaine.comptes import CompteBancaire
from kampusbank.domaine.exceptions import CompteIntrouvableError
from kampusbank.domaine.user import User
from kampusbank.persistance.depot import Depot


def compte_du_client(depot: Depot, client: User, compte_id: int) -> CompteBancaire:
    """Renvoie le compte s'il appartient au client.

    Le message est le même que le compte n'existe pas ou qu'il appartienne à
    quelqu'un d'autre : on ne révèle pas l'existence des comptes des autres.
    """
    compte = depot.trouver_compte(compte_id)
    if compte is None or compte.proprietaire_id != client.id:
        raise CompteIntrouvableError(
            "Ce compte n'existe pas ou ne vous appartient pas."
        )
    return compte
