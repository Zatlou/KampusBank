"""Unicité de l'email (RG14), partagée par l'inscription et le profil."""

from kampusbank.domaine.exceptions import EmailDejaUtiliseError
from kampusbank.domaine.validation import valider_email
from kampusbank.persistance.depot import Depot


def exiger_email_disponible(
    depot: Depot, email: str, id_proprietaire: int | None = None
) -> str:
    """Renvoie l'email validé s'il n'appartient à personne d'autre.

    id_proprietaire désigne l'utilisateur qui garde le droit d'utiliser cet
    email : lui-même, quand il modifie son profil sans changer d'email.
    """
    email = valider_email(email)
    existant = depot.trouver_utilisateur_par_email(email)
    if existant is not None and existant.id != id_proprietaire:
        raise EmailDejaUtiliseError(f"L'email « {email} » est déjà utilisé.")
    return email
