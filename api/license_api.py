"""
api.license_api
================

Blueprint HTTP exposant au frontend (JS/HTML) le système de licence défini
dans le package `licensing/`. Ce fichier ne contient AUCUNE logique de
sécurité : il ne fait que valider la forme des requêtes entrantes et
traduire les résultats de `licensing.license_manager` / `licensing.challenge`
en réponses JSON. Toute la décision (signature ECDSA, correspondance HWID,
expiration, anti-recul d'horloge) reste dans `licensing/`.

Routes :
    POST /api/activate           -> active une licence fournie en Base64
    GET  /api/license/status     -> état courant de la licence (pour l'UI)
    GET  /api/license/challenge  -> code d'installation + HWID courant (QR code)
"""

from flask import Blueprint, request, jsonify

from licensing.license_manager import activate, get_status, STATUS_VALID
from licensing.challenge import generate_installation_code
from licensing.hardware_id import get_hwid

license_bp = Blueprint('license', __name__, url_prefix='/api')

# Statuts qui correspondent à une erreur "attendue" côté client (mauvaise clé,
# mauvaise machine, licence expirée...) : on répond 400 plutôt que 200/500,
# pour que le JS puisse distinguer "requête invalide" d'un simple refus métier
# tout en gardant le corps JSON exploitable dans les deux cas.
_CLIENT_ERROR_STATUSES = {
    'invalid',
    'hwid_mismatch',
    'expired',
    'clock_rollback_detected',
}


@license_bp.route('/activate', methods=['POST'])
def activate_route():
    """
    Active la licence transmise par le formulaire du frontend.

    Corps attendu (JSON) :
        { "license_key": "<chaîne Base64 fournie par l'administrateur>" }

    Réponse JSON :
        {
          "success": bool,
          "status": "valid" | "invalid" | "hwid_mismatch" | "expired" | ...,
          "message": str,
          "license": {"sch": ..., "hwid": ..., "exp": ...} | None
        }
    """
    try:
        data = request.get_json(silent=True) or {}
        license_key = (data.get('license_key') or data.get('license') or '').strip()

        if not license_key:
            return jsonify({
                'success': False,
                'status': 'invalid',
                'message': "Aucune clé de licence fournie.",
                'license': None,
            }), 400

        result = activate(license_key)
        is_valid = result.get('status') == STATUS_VALID
        http_code = 200 if is_valid else (400 if result.get('status') in _CLIENT_ERROR_STATUSES else 500)

        return jsonify({
            'success': is_valid,
            'status': result.get('status'),
            'message': result.get('message'),
            'license': result.get('license'),
        }), http_code

    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'invalid',
            'message': f"Erreur inattendue lors de l'activation : {e}",
            'license': None,
        }), 500


@license_bp.route('/license/status', methods=['GET'])
def license_status_route():
    """
    Renvoie l'état courant de la licence installée sur cette machine, pour
    que le frontend sache quoi afficher (application débloquée, écran de
    blocage avec formulaire d'activation, message d'expiration, etc).

    Réponse JSON :
        {
          "success": bool,
          "status": "valid" | "no_license" | "expired" | "hwid_mismatch"
                     | "clock_rollback_detected" | "invalid",
          "message": str,
          "license": {"sch": ..., "hwid": ..., "exp": ..., "activated_at": ...} | None
        }

    Cette route ne doit jamais être bloquée par le middleware d'application
    (@app.before_request) : c'est elle qui permet au JS de savoir qu'il faut
    afficher l'écran de blocage plutôt que de tenter d'appeler les autres
    endpoints métier.
    """
    try:
        result = get_status()
        return jsonify({
            'success': result.get('status') == STATUS_VALID,
            'status': result.get('status'),
            'message': result.get('message'),
            'license': result.get('license'),
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'invalid',
            'message': f"Erreur lors de la lecture du statut de licence : {e}",
            'license': None,
        }), 500


@license_bp.route('/license/challenge', methods=['GET'])
def license_challenge_route():
    """
    Renvoie le HWID courant de la machine ainsi que le code d'installation
    dérivé (court, lisible), pour que le frontend l'affiche en gros
    caractères et/ou génère un QR code (ex: via qrcode.js). Le proviseur
    transmet ensuite ce code à l'administrateur (photo/WhatsApp) pour
    obtenir une nouvelle licence signée correspondant à cette machine.

    Ce code n'est pas un secret : il ne sert qu'à transmettre le HWID de
    façon fiable et lisible par un humain, la sécurité réelle reposant
    entièrement sur la signature ECDSA vérifiée lors de l'activation.

    Réponse JSON :
        {
          "success": true,
          "hwid": "001a2b3c4d5e",
          "installation_code": "A3F9C21B"
        }
    """
    try:
        hwid = get_hwid()
        installation_code = generate_installation_code(hwid)
        return jsonify({
            'success': True,
            'hwid': hwid,
            'installation_code': installation_code,
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Erreur lors de la génération du code d'installation : {e}",
        }), 500