"""
licensing.challenge
====================

Génère le "code d'installation" affiché au proviseur lorsqu'aucune licence
valide n'est installée (premier démarrage) ou que le matériel a changé
(nouvel ordinateur -> nouveau HWID).

Ce code n'est PAS un secret et ne fait partie d'aucune chaîne de confiance :
son seul rôle est de donner à l'administrateur, de façon fiable et sans
connexion internet, le HWID exact de la machine à qui il doit émettre une
nouvelle licence (par WhatsApp/photo/QR code). La vraie sécurité reste
entièrement portée par la signature ECDSA vérifiée dans crypto_utils.
"""

import hashlib
import hmac

from .hardware_id import get_hwid

# Sel fixe, non secret : il ne fait qu'éviter que le code d'installation
# soit un simple hash brut du HWID (ce qui n'aurait aucune conséquence de
# sécurité ici, mais évite la confusion visuelle avec le HWID lui-même).
_INSTALL_CODE_SALT = b'gestionnaire-mono/installation-code/v1'

DEFAULT_CODE_LENGTH = 8


def generate_installation_code(hwid: str = None, length: int = DEFAULT_CODE_LENGTH) -> str:
    """
    Génère un code court et lisible (par défaut 8 caractères hexadécimaux
    majuscules) dérivé du HWID de la machine locale.

    Args:
        hwid: HWID à utiliser. Si omis, on lit celui de la machine courante
            via hardware_id.get_hwid().
        length: longueur du code renvoyé (6 à 8 caractères recommandés :
            assez court pour être recopié/photographié sans erreur, assez
            long pour limiter les collisions visuelles entre écoles).

    Returns:
        Une chaîne hexadécimale majuscule, ex: 'A3F9C21B'.

    Note: ce code est déterministe (même HWID -> même code), ce qui permet
    à l'administrateur de le régénérer lui-même pour vérification si besoin,
    à condition de connaître le HWID transmis par ailleurs.
    """
    hwid = (hwid or get_hwid()).lower()
    digest = hmac.new(_INSTALL_CODE_SALT, hwid.encode('utf-8'), hashlib.sha256).hexdigest()
    return digest[:length].upper()