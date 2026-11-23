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


class MontantInvalideError(DonneeInvalideError):
    """Le montant n'est pas un nombre positif à 2 décimales au plus (RG17)."""


class IbanInvalideError(DonneeInvalideError):
    """L'IBAN saisi n'a pas le format KampusBank (RG4)."""


class TypeCompteInconnuError(KampusBankError):
    """Le type de compte demandé n'existe pas."""


class CompteIntrouvableError(KampusBankError):
    """Le compte n'existe pas, ou n'appartient pas au client connecté."""


class CompteBloqueError(KampusBankError):
    """Le compte est bloqué : aucune opération possible, ni débit ni crédit (RG7)."""


class CompteNonVideError(KampusBankError):
    """Un compte ne peut être supprimé que si son solde vaut 0,00 € (RG6)."""


class SoldeInsuffisantError(KampusBankError):
    """Le solde deviendrait négatif (RG9, RG10)."""


class LimiteOperationError(KampusBankError):
    """Le montant sort des limites de l'opération (RG8 à RG10)."""


class PlafondDepasseError(KampusBankError):
    """Le crédit ferait dépasser le plafond du compte (Livret A, PEL)."""


class RetraitInterditError(KampusBankError):
    """Ce type de compte n'autorise pas les retraits (PEL)."""


class VirementInvalideError(KampusBankError):
    """Le compte source et le compte destinataire sont identiques."""


class AnnulationImpossibleError(KampusBankError):
    """La dernière opération du compte ne peut pas être annulée (RG13)."""


class SuppressionClientImpossibleError(KampusBankError):
    """Le client ne peut pas être supprimé (comptes non vides, administrateur)."""


class ClientIntrouvableError(KampusBankError):
    """Le client demandé n'existe pas."""
