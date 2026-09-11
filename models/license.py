"""
models.license
================

Modèle SQLAlchemy représentant l'état de la licence, persisté dans la même
base applicative (bulletins.db) que le reste des données métier.

Positionnement par rapport à `licensing.license_manager` :
---------------------------------------------------------
Le store SQLite indépendant de `licensing.license_manager` (fichier séparé
`.license_store.sqlite3`) reste la source de vérité chargée tôt, avant même
l'initialisation de SQLAlchemy — c'est lui qui doit continuer à piloter le
middleware `@app.before_request`. Ce modèle-ci est un registre complémentaire,
utile pour :
  - l'audit et le renvoi du JSON signé tel que reçu (license_payload) ;
  - la détection de falsification DIRECTE de bulletins.db via un éditeur
    SQLite externe : si quelqu'un modifie last_seen_timestamp à la main dans
    ce fichier (plutôt que de reculer l'horloge système, déjà couvert par
    license_manager), l'integrity_hmac stocké à côté ne correspondra plus
    à la valeur recalculée -> verify_integrity() renverra False.

L'integrity_hmac ne protège PAS contre quelqu'un qui aurait accès au secret
local (il vit dans instance/.license_hmac.key, à côté de la base) : il
protège contre une modification "à la main" par un utilisateur qui ne
connaît que le contenu de bulletins.db, pas le fonctionnement interne de
l'application.
"""

import hashlib
import hmac
import os
import time
from pathlib import Path

from models import db

_HMAC_KEY_FILENAME = '.license_hmac.key'
_hmac_secret_cache: bytes | None = None


def _load_or_create_hmac_secret() -> bytes:
    """
    Charge le secret local utilisé pour calculer integrity_hmac, ou le crée
    s'il n'existe pas encore (32 octets aléatoires, écrits une seule fois).

    Ce secret est volontairement DISTINCT de app.config['SECRET_KEY'] (qui
    sert aux sessions Flask et a une valeur par défaut faible en dev) : on ne
    veut pas qu'une valeur par défaut connue de tous affaiblisse la détection
    de falsification.
    """
    global _hmac_secret_cache
    if _hmac_secret_cache is not None:
        return _hmac_secret_cache

    try:
        from config import INSTANCE_DIR
        instance_dir = Path(INSTANCE_DIR)
    except ImportError:
        instance_dir = Path(__file__).resolve().parent.parent / 'instance'
        instance_dir.mkdir(exist_ok=True)

    secret_path = instance_dir / _HMAC_KEY_FILENAME

    if secret_path.exists():
        _hmac_secret_cache = secret_path.read_bytes()
        return _hmac_secret_cache

    secret = os.urandom(32)
    secret_path.write_bytes(secret)
    try:
        os.chmod(secret_path, 0o600)
    except OSError:
        # Pas critique (ex: certains systèmes de fichiers Windows) : le
        # fichier reste discret même sans permissions restreintes.
        pass

    _hmac_secret_cache = secret
    return secret


class LicenseState(db.Model):
    """
    État de licence courant, en ligne unique (id = 1), miroir audité du
    store indépendant de licensing.license_manager.
    """
    __tablename__ = 'license_state'

    id = db.Column(db.Integer, primary_key=True)

    # JSON signé stocké tel quel (Base64 ou JSON brut, au choix de l'appelant),
    # pour pouvoir le ré-afficher / le renvoyer par WhatsApp sans redemander
    # la clé au proviseur.
    license_payload = db.Column(db.Text, nullable=False)

    school_id = db.Column(db.String(100), nullable=False)
    hwid = db.Column(db.String(64), nullable=False)

    # Timestamps epoch (secondes), cohérents avec licensing.license_manager
    expires_at = db.Column(db.Integer, nullable=False)
    activated_at = db.Column(db.Integer, nullable=False)

    # Protection anti-recul d'horloge : mis à jour à chaque requête.
    last_seen_timestamp = db.Column(db.Integer, nullable=False)

    # HMAC-SHA256 hex de last_seen_timestamp, pour détecter une modification
    # directe de la ligne via un éditeur SQLite externe.
    integrity_hmac = db.Column(db.String(64), nullable=False)

    __table_args__ = (
        db.CheckConstraint('id = 1', name='ck_license_state_singleton'),
    )

    # -- Intégrité ---------------------------------------------------------

    @staticmethod
    def compute_hmac(last_seen_timestamp: int) -> str:
        secret = _load_or_create_hmac_secret()
        message = str(int(last_seen_timestamp)).encode('utf-8')
        return hmac.new(secret, message, hashlib.sha256).hexdigest()

    def refresh_integrity(self) -> None:
        """Recalcule integrity_hmac à partir de last_seen_timestamp courant.
        À appeler après toute modification de last_seen_timestamp, avant commit."""
        self.integrity_hmac = self.compute_hmac(self.last_seen_timestamp)

    def verify_integrity(self) -> bool:
        """
        Renvoie False si last_seen_timestamp (ou integrity_hmac lui-même) a
        été modifié directement en base, hors du code applicatif.
        """
        if not self.integrity_hmac:
            return False
        expected = self.compute_hmac(self.last_seen_timestamp)
        return hmac.compare_digest(expected, self.integrity_hmac)

    # -- Cycle de vie --------------------------------------------------

    def touch(self, now: int | None = None) -> None:
        """
        Enregistre l'heure courante comme dernier timestamp vu et recalcule
        integrity_hmac en conséquence. Ne fait PAS le commit (à la charge de
        l'appelant, généralement dans le middleware @app.before_request).
        """
        self.last_seen_timestamp = int(now if now is not None else time.time())
        self.refresh_integrity()

    @classmethod
    def get_singleton(cls) -> 'LicenseState | None':
        return cls.query.get(1)

    @classmethod
    def upsert(cls, *, license_payload: str, school_id: str, hwid: str,
               expires_at: int, activated_at: int | None = None,
               now: int | None = None) -> 'LicenseState':
        """
        Crée ou met à jour la ligne unique de licence (id = 1). Ne fait PAS
        le commit : à appeler puis db.session.commit() côté appelant, pour
        rester cohérent avec le reste des transactions Flask.
        """
        now = int(now if now is not None else time.time())
        activated_at = int(activated_at if activated_at is not None else now)

        state = cls.get_singleton()
        if state is None:
            state = cls(id=1)
            db.session.add(state)

        state.license_payload = license_payload
        state.school_id = school_id
        state.hwid = hwid
        state.expires_at = int(expires_at)
        state.activated_at = activated_at
        state.touch(now)

        return state

    # -- Sérialisation -------------------------------------------------

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'school_id': self.school_id,
            'hwid': self.hwid,
            'expires_at': self.expires_at,
            'activated_at': self.activated_at,
            'last_seen_timestamp': self.last_seen_timestamp,
            'integrity_ok': self.verify_integrity(),
        }