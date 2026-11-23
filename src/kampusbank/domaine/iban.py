"""IBAN KampusBank (RG4) : FR76-KPBK-XXXX-XXXX-XXXX-XXXX-XXX, X étant un chiffre."""

import random
import re

from kampusbank.domaine.exceptions import IbanInvalideError

_PREFIXE = "FR76KPBK"
_NOMBRE_DE_CHIFFRES = 19
_TAILLES_DES_GROUPES = (4, 4, 4, 4, 3)
_MOTIF_COMPACT = re.compile(rf"{_PREFIXE}[0-9]{{{_NOMBRE_DE_CHIFFRES}}}")


def generer_iban(hasard: random.Random) -> str:
    """Tire 19 chiffres au hasard et renvoie l'IBAN au format officiel.

    L'unicité n'est pas garantie ici : c'est le service qui vérifie que
    l'IBAN tiré n'existe pas déjà, et qui en tire un autre sinon.
    """
    chiffres = "".join(str(hasard.randrange(10)) for _ in range(_NOMBRE_DE_CHIFFRES))
    return _formater(_PREFIXE + chiffres)


def normaliser_iban(texte: str) -> str:
    """Accepte un IBAN saisi avec ou sans tirets ni espaces, et le remet en forme."""
    compact = re.sub(r"[\s-]", "", texte).upper()
    if not _MOTIF_COMPACT.fullmatch(compact):
        raise IbanInvalideError(
            f"« {texte} » n'est pas un IBAN KampusBank "
            "(format FR76-KPBK-XXXX-XXXX-XXXX-XXXX-XXX)."
        )
    return _formater(compact)


def _formater(compact: str) -> str:
    morceaux = [compact[:4], compact[4:8]]
    position = 8
    for taille in _TAILLES_DES_GROUPES:
        morceaux.append(compact[position : position + taille])
        position += taille
    return "-".join(morceaux)
