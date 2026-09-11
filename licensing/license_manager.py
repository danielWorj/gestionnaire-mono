"""
licensing.license_manager
==========================

Cœur logique du système de licence : stockage local (SQLite), activation,
et détection de recul d'horloge.

Le stockage est volontairement fait en SQLite "brut" (module sqlite3 de la
stdlib, indépendant de Flask-SQLAlchemy) pour deux raisons :
  1. le statut de la licence doit pouvoir être vérifié très tôt (avant même
     que l'application Flask/SQLAlchemy soit pleinement initialisée) ;
  2. on ne veut pas que la licence dépende du même fichier applicatif
     (bulletins.db) qu'un utilisateur pourrait être tenté de manipuler.
"""

import sqlite3
import time
from contextlib import closing
from pathlib import Path

from .crypto_utils import LicenseFormatError, LicenseSignatureError, decode_license
from .hardware_id import get_hwid

# On réutilise le dossier "instance" persistant de l'application (celui qui
# vit à côté de l'exécutable, cf config.py) si disponible, pour que la base
# de licence survive aux mises à jour de l'application. Sinon, repli local.
try:
    from config import INSTANCE_DIR as _APP_INSTANCE_DIR
    _INSTANCE_DIR = _APP_INSTANCE_DIR
except ImportError:
    _INSTANCE_DIR = Path(__file__).resolve().parent / '.instance'
    _INSTANCE_DIR.mkdir(exist_ok=True)

# Nom de fichier discret, préfixé d'un point : on ne cherche pas à cacher la
# base au proviseur (elle est de toute façon protégée par les signatures ECDSA
# et non par la discrétion de son nom), mais on évite qu'elle saute aux yeux.
LICENSE_DB_PATH = Path(_INSTANCE_DIR) / '.license_store.sqlite3'

# Tolère de petits ajustements d'horloge (ex : synchronisation NTP, fuseau
# horaire) sans déclencher un blocage anti-fraude sur un simple bruit de fond.
CLOCK_ROLLBACK_TOLERANCE_SECONDS = 5 * 60

STATUS_VALID = 'valid'
STATUS_EXPIRED = 'expired'
STATUS_HWID_MISMATCH = 'hwid_mismatch'
STATUS_NO_LICENSE = 'no_license'
STATUS_CLOCK_ROLLBACK = 'clock_rollback_detected'
STATUS_INVALID = 'invalid'


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(LICENSE_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    with closing(_get_connection()) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS license (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                sch TEXT NOT NULL,
                hwid TEXT NOT NULL,
                exp INTEGER NOT NULL,
                activated_at INTEGER NOT NULL,
                raw_license TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS clock_watch (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                last_seen_timestamp INTEGER NOT NULL
            )
        ''')
        conn.commit()


_init_db()


def load_current_license() -> dict | None:
    """Renvoie la licence actuellement stockée : {sch, hwid, exp, activated_at},
    ou None si aucune licence n'a jamais été activée sur cette machine."""
    with closing(_get_connection()) as conn:
        row = conn.execute(
            'SELECT sch, hwid, exp, activated_at FROM license WHERE id = 1'
        ).fetchone()
    return dict(row) if row is not None else None


def _store_license(payload: dict, raw_license: str) -> None:
    now = int(time.time())
    with closing(_get_connection()) as conn:
        conn.execute('''
            INSERT INTO license (id, sch, hwid, exp, activated_at, raw_license)
            VALUES (1, :sch, :hwid, :exp, :now, :raw)
            ON CONFLICT(id) DO UPDATE SET
                sch = excluded.sch,
                hwid = excluded.hwid,
                exp = excluded.exp,
                activated_at = excluded.activated_at,
                raw_license = excluded.raw_license
        ''', {**payload, 'now': now, 'raw': raw_license})
        conn.commit()


def _touch_clock(now: int) -> None:
    """Enregistre l'heure système courante comme référence anti-recul. On ne
    garde jamais qu'un timestamp inférieur à celui déjà connu : le "plus
    grand timestamp jamais vu" est la seule chose qui compte."""
    with closing(_get_connection()) as conn:
        conn.execute('''
            INSERT INTO clock_watch (id, last_seen_timestamp)
            VALUES (1, :now)
            ON CONFLICT(id) DO UPDATE SET
                last_seen_timestamp = MAX(last_seen_timestamp, excluded.last_seen_timestamp)
        ''', {'now': now})
        conn.commit()


def check_clock_integrity() -> bool:
    """
    Compare l'heure système actuelle au dernier timestamp connu et enregistré
    en base. Si l'heure actuelle est significativement ANTÉRIEURE au dernier
    timestamp vu, l'horloge a probablement été reculée volontairement (pour
    contourner une expiration) : renvoie False.

    Si tout va bien, met à jour le timestamp de référence et renvoie True.
    Doit être appelée à chaque requête (middleware @app.before_request) pour
    que le "dernier timestamp connu" progresse régulièrement.
    """
    now = int(time.time())

    with closing(_get_connection()) as conn:
        row = conn.execute(
            'SELECT last_seen_timestamp FROM clock_watch WHERE id = 1'
        ).fetchone()

    if row is None:
        _touch_clock(now)
        return True

    last_seen = row['last_seen_timestamp']

    if now < last_seen - CLOCK_ROLLBACK_TOLERANCE_SECONDS:
        return False

    _touch_clock(now)
    return True


def activate(license_b64: str) -> dict:
    """
    Tente d'activer une licence fournie en Base64 (typiquement collée dans le
    formulaire du frontend, transmis via POST /api/activate).

    Déroulé strict : signature -> correspondance matérielle -> expiration ->
    enregistrement en base. Ne lève pas d'exception pour les cas d'échec
    "attendus" : tout se traduit par un dict {'status': ..., 'message': ...}
    directement exploitable par la route Flask (ex: jsonify(result)).
    """
    try:
        payload = decode_license(license_b64)
    except (LicenseFormatError, LicenseSignatureError) as exc:
        return {'status': STATUS_INVALID, 'message': str(exc), 'license': None}

    local_hwid = get_hwid()
    if payload['hwid'].lower() != local_hwid.lower():
        return {
            'status': STATUS_HWID_MISMATCH,
            'message': "Cette licence a été émise pour un autre ordinateur. "
                       "Utilisez le code d'installation de CETTE machine pour "
                       "obtenir une nouvelle licence.",
            'license': None,
        }

    now = int(time.time())
    if payload['exp'] < now:
        return {
            'status': STATUS_EXPIRED,
            'message': "Cette licence est expirée. Contactez l'administrateur pour la renouveler.",
            'license': None,
        }

    _store_license(payload, license_b64)
    _touch_clock(now)

    return {
        'status': STATUS_VALID,
        'message': "Licence activée avec succès.",
        'license': payload,
    }


def get_status() -> dict:
    """
    Évalue l'état courant de la licence installée sur cette machine, sans
    rien modifier hormis la mise à jour du témoin anti-recul d'horloge.

    À appeler à chaque requête entrante (middleware) pour décider de bloquer
    ou non l'accès à l'application.

    Returns:
        dict {'status': un des STATUS_*, 'message': str, 'license': dict|None}
    """
    if not check_clock_integrity():
        return {
            'status': STATUS_CLOCK_ROLLBACK,
            'message': "L'horloge du système a reculé par rapport à la dernière "
                       "utilisation connue. Accès bloqué par sécurité.",
            'license': load_current_license(),
        }

    license_data = load_current_license()
    if license_data is None:
        return {'status': STATUS_NO_LICENSE, 'message': "Aucune licence n'est installée.", 'license': None}

    local_hwid = get_hwid()
    if license_data['hwid'].lower() != local_hwid.lower():
        return {
            'status': STATUS_HWID_MISMATCH,
            'message': "La licence installée ne correspond pas à cet ordinateur.",
            'license': license_data,
        }

    if int(license_data['exp']) < int(time.time()):
        return {
            'status': STATUS_EXPIRED,
            'message': "L'abonnement de cette école a expiré.",
            'license': license_data,
        }

    return {'status': STATUS_VALID, 'message': "Licence valide.", 'license': license_data}