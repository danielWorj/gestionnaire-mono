"""
licensing.crypto_utils
=======================

Décodage et vérification cryptographique des licences.

Format d'une licence, AVANT encodage Base64 (c'est un JSON UTF-8) :

    {
        "payload": {
            "sch": "ECOLE-YAOUNDE-042",
            "hwid": "001a2b3c4d5e",
            "exp": 1780000000
        },
        "signature": "<signature ECDSA/SHA-256 au format DER, encodée en Base64>"
    }

La signature porte sur la sérialisation JSON canonique du champ "payload"
(clés triées, séparateurs compacts, UTF-8) — c'est exactement ce que
`decode_license` recalcule ici pour vérifier. admin_tools/issue_license.py
doit signer avec la même sérialisation, sans quoi la vérification échouera.
"""

import base64
import json

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from .public_key import PUBLIC_KEY_PEM

REQUIRED_FIELDS = ('sch', 'hwid', 'exp')


class LicenseFormatError(Exception):
    """La chaîne fournie n'est pas une licence exploitable (Base64/JSON malformé,
    champ manquant...). Ne présume rien sur son authenticité."""


class LicenseSignatureError(Exception):
    """Le contenu de la licence a pu être décodé, mais sa signature ECDSA
    ne correspond pas : la licence est invalide ou a été altérée."""


_public_key = serialization.load_pem_public_key(PUBLIC_KEY_PEM)


def _canonical_payload_bytes(payload: dict) -> bytes:
    """Sérialisation JSON canonique utilisée à la fois pour signer (côté admin)
    et pour vérifier (ici) : clés triées, pas d'espaces, UTF-8."""
    return json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')


def verify_signature(payload: bytes, signature: bytes) -> bool:
    """
    Vérifie qu'une signature ECDSA/SHA-256 (format DER) correspond bien au
    payload donné (bytes), avec la clé publique embarquée.

    Ne lève jamais d'exception métier : renvoie True/False. Les erreurs
    d'entrée totalement invalides (mauvais type...) restent des exceptions
    Python normales, volontairement non capturées ici.
    """
    try:
        _public_key.verify(signature, payload, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False


def decode_license(b64_string: str) -> dict:
    """
    Décode une clé de licence fournie en Base64 par l'utilisateur, vérifie
    sa signature ECDSA, et renvoie le payload validé.

    Args:
        b64_string: la clé de licence telle que saisie/collée par le proviseur.

    Returns:
        dict {'sch': str, 'hwid': str, 'exp': int} si tout est valide.

    Raises:
        LicenseFormatError: JSON/Base64 malformé ou champ requis manquant.
        LicenseSignatureError: la signature ne correspond pas au contenu.
    """
    if not b64_string or not isinstance(b64_string, str):
        raise LicenseFormatError("Aucune clé de licence fournie.")

    try:
        raw = base64.b64decode(b64_string.strip(), validate=True)
        envelope = json.loads(raw)
    except Exception as exc:
        raise LicenseFormatError(f"Clé de licence illisible : {exc}") from exc

    if not isinstance(envelope, dict) or 'payload' not in envelope or 'signature' not in envelope:
        raise LicenseFormatError("Structure de licence invalide (payload/signature manquant).")

    payload = envelope['payload']
    if not isinstance(payload, dict):
        raise LicenseFormatError("Le contenu (payload) de la licence est invalide.")

    missing = [f for f in REQUIRED_FIELDS if f not in payload]
    if missing:
        raise LicenseFormatError(f"Champ(s) manquant(s) dans la licence : {', '.join(missing)}")

    try:
        signature = base64.b64decode(envelope['signature'], validate=True)
    except Exception as exc:
        raise LicenseFormatError(f"Signature illisible : {exc}") from exc

    payload_bytes = _canonical_payload_bytes(payload)

    if not verify_signature(payload_bytes, signature):
        raise LicenseSignatureError("La signature de la licence est invalide : "
                                     "elle a peut-être été altérée ou n'a pas été émise par l'administrateur.")

    return {
        'sch': str(payload['sch']),
        'hwid': str(payload['hwid']),
        'exp': int(payload['exp']),
    }