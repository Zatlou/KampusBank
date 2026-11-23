"""Hachage des mots de passe avec bcrypt (RG1)."""

import bcrypt

_OCTETS_MAX = 72


class HacheurMotDePasse:
    """Transforme un mot de passe en empreinte bcrypt et la vérifie.

    Le coût est injecté : 12 en production (lent exprès, contre les attaques
    par force brute), 4 dans les tests pour qu'ils restent rapides.
    """

    def __init__(self, cout: int) -> None:
        self._cout = cout

    def hacher(self, mot_de_passe: str) -> str:
        """Renvoie l'empreinte du mot de passe, avec un sel aléatoire intégré."""
        sel = bcrypt.gensalt(rounds=self._cout)
        return bcrypt.hashpw(mot_de_passe.encode("utf-8"), sel).decode("ascii")

    def verifier(self, mot_de_passe: str, empreinte: str) -> bool:
        """Vrai si le mot de passe correspond à l'empreinte."""
        octets = mot_de_passe.encode("utf-8")
        if len(octets) > _OCTETS_MAX:
            return False
        return bcrypt.checkpw(octets, empreinte.encode("ascii"))
