"""Exceptions métier : chaque violation d'une règle de gestion en lève une (EC4).

Toutes dérivent de KampusBankError : l'interface n'a qu'une seule exception à
intercepter pour afficher le message à l'utilisateur.
"""


class KampusBankError(Exception):
    """Exception commune à toutes les erreurs métier de KampusBank."""


class DonneeInvalideError(KampusBankError):
    """Une donnée saisie ne respecte pas son format (RG14 à RG17)."""


class ChampObligatoireError(DonneeInvalideError):
    """Un champ obligatoire est vide."""


class EmailInvalideError(DonneeInvalideError):
    """L'email n'a pas un format valide (RG14)."""


class TelephoneInvalideError(DonneeInvalideError):
    """Le téléphone ne compte pas exactement 10 chiffres (RG15)."""


class MotDePasseInvalideError(DonneeInvalideError):
    """Le mot de passe est trop faible (RG16)."""


class DateInvalideError(DonneeInvalideError):
    """La date saisie n'est pas au format JJ/MM/AAAA."""


class EmailDejaUtiliseError(KampusBankError):
    """Un autre utilisateur possède déjà cet email (RG14)."""


class IdentifiantsInvalidesError(KampusBankError):
    """L'email ou le mot de passe est incorrect."""


class UtilisateurBloqueError(KampusBankError):
    """Le compte utilisateur est bloqué après trop d'échecs de connexion (RG3)."""


class NonConnecteError(KampusBankError):
    """La fonction demandée exige un utilisateur connecté (RG2)."""


class AccesRefuseError(KampusBankError):
    """La fonction demandée est réservée aux administrateurs (RG2)."""
