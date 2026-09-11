"""
licensing
=========

Système de licence hors-ligne pour l'application de gestion scolaire.

Ce package ne contient QUE la logique côté école (vérification). La clé
privée qui permet de GÉNÉRER des licences reste sur le poste d'administration
distant (voir admin_tools/, à la racine du projet, qui ne doit jamais être
livré aux écoles).

Usage typique dans app.py :

    from licensing.license_manager import get_status, activate, STATUS_VALID

    @app.before_request
    def enforce_license():
        if request.endpoint in ('static', 'activate_route'):
            return
        status = get_status()
        if status['status'] != STATUS_VALID:
            return render_template('licence_bloquee.html', status=status), 403

    @app.route('/api/activate', methods=['POST'])
    def activate_route():
        result = activate(request.json.get('license_key', ''))
        return result
"""

from .license_manager import (
    activate,
    get_status,
    load_current_license,
    check_clock_integrity,
    STATUS_VALID,
    STATUS_EXPIRED,
    STATUS_HWID_MISMATCH,
    STATUS_NO_LICENSE,
    STATUS_CLOCK_ROLLBACK,
    STATUS_INVALID,
)
from .hardware_id import get_hwid
from .challenge import generate_installation_code

__all__ = [
    'activate',
    'get_status',
    'load_current_license',
    'check_clock_integrity',
    'get_hwid',
    'generate_installation_code',
    'STATUS_VALID',
    'STATUS_EXPIRED',
    'STATUS_HWID_MISMATCH',
    'STATUS_NO_LICENSE',
    'STATUS_CLOCK_ROLLBACK',
    'STATUS_INVALID',
]