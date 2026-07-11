from flask import Blueprint, request, jsonify
from services.emploi_du_temps_service import CreneauHoraireService, HoraireService
from datetime import time

emploi_du_temps_bp = Blueprint('emploi_du_temps', __name__, url_prefix='/api/emploi-du-temps')


# ==================== CRÉNEAUX HORAIRES ====================

@emploi_du_temps_bp.route('/creneaux', methods=['GET'])
def get_all_creneaux():
    """Récupérer tous les créneaux horaires"""
    try:
        creneaux = CreneauHoraireService.get_all()
        return jsonify({
            'success': True,
            'data': [creneau.to_dict() for creneau in creneaux],
            'count': len(creneaux)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@emploi_du_temps_bp.route('/creneaux/<int:id>', methods=['GET'])
def get_creneau_by_id(id):
    """Récupérer un créneau par ID"""
    try:
        creneau = CreneauHoraireService.get_by_id(id)
        if creneau:
            return jsonify({'success': True, 'data': creneau.to_dict()}), 200
        return jsonify({'success': False, 'error': 'Créneau non trouvé'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@emploi_du_temps_bp.route('/creneaux', methods=['POST'])
def create_creneau():
    """Créer un nouveau créneau horaire"""
    try:
        data = request.get_json()
        
        # Validation des champs requis
        required_fields = ['libelle', 'heure_debut', 'heure_fin', 'ordre']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400
        
        # Conversion des heures (format ISO "HH:MM:SS" ou "HH:MM")
        if isinstance(data['heure_debut'], str):
            data['heure_debut'] = time.fromisoformat(data['heure_debut'])
        if isinstance(data['heure_fin'], str):
            data['heure_fin'] = time.fromisoformat(data['heure_fin'])
        
        creneau = CreneauHoraireService.create(data)
        return jsonify({
            'success': True,
            'data': creneau.to_dict(),
            'message': 'Créneau horaire créé'
        }), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@emploi_du_temps_bp.route('/creneaux/<int:id>', methods=['PUT'])
def update_creneau(id):
    """Mettre à jour un créneau horaire"""
    try:
        data = request.get_json()
        
        # Conversion des heures si présentes
        if 'heure_debut' in data and isinstance(data['heure_debut'], str):
            data['heure_debut'] = time.fromisoformat(data['heure_debut'])
        if 'heure_fin' in data and isinstance(data['heure_fin'], str):
            data['heure_fin'] = time.fromisoformat(data['heure_fin'])
        
        creneau = CreneauHoraireService.update(id, data)
        if creneau:
            return jsonify({
                'success': True,
                'data': creneau.to_dict(),
                'message': 'Créneau horaire mis à jour'
            }), 200
        return jsonify({'success': False, 'error': 'Créneau non trouvé'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@emploi_du_temps_bp.route('/creneaux/<int:id>', methods=['DELETE'])
def delete_creneau(id):
    """Supprimer un créneau horaire"""
    try:
        if CreneauHoraireService.delete(id):
            return jsonify({'success': True, 'message': 'Créneau supprimé'}), 200
        return jsonify({'success': False, 'error': 'Créneau non trouvé'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== HORAIRES (EMPLOI DU TEMPS) ====================

@emploi_du_temps_bp.route('/horaires', methods=['GET'])
def get_all_horaires():
    """Récupérer tous les horaires"""
    try:
        horaires = HoraireService.get_all()
        return jsonify({
            'success': True,
            'data': [horaire.to_dict() for horaire in horaires],
            'count': len(horaires)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@emploi_du_temps_bp.route('/horaires/<int:id>', methods=['GET'])
def get_horaire_by_id(id):
    """Récupérer un horaire par ID"""
    try:
        horaire = HoraireService.get_by_id(id)
        if horaire:
            return jsonify({'success': True, 'data': horaire.to_dict()}), 200
        return jsonify({'success': False, 'error': 'Horaire non trouvé'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@emploi_du_temps_bp.route('/classes/<int:classe_id>/annees/<int:annee_id>/horaires', methods=['GET'])
def get_horaires_classe_annee(classe_id, annee_id):
    """Récupérer l'emploi du temps d'une classe pour une année scolaire"""
    try:
        horaires = HoraireService.get_by_classe_annee(classe_id, annee_id)
        return jsonify({
            'success': True,
            'data': [horaire.to_dict() for horaire in horaires],
            'count': len(horaires)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@emploi_du_temps_bp.route('/enseignants/<int:enseignant_id>/annees/<int:annee_id>/horaires', methods=['GET'])
def get_horaires_enseignant_annee(enseignant_id, annee_id):
    """Récupérer l'emploi du temps d'un enseignant pour une année scolaire"""
    try:
        horaires = HoraireService.get_by_enseignant_annee(enseignant_id, annee_id)
        return jsonify({
            'success': True,
            'data': [horaire.to_dict() for horaire in horaires],
            'count': len(horaires)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@emploi_du_temps_bp.route('/horaires', methods=['POST'])
def create_horaire():
    """Créer un nouvel horaire"""
    try:
        data = request.get_json()
        
        # Validation des champs requis
        required_fields = ['matiere_classe_id', 'annee_scolaire_id', 'jour_semaine', 'creneau_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400
        
        horaire = HoraireService.create(data)
        return jsonify({
            'success': True,
            'data': horaire.to_dict(),
            'message': 'Horaire créé'
        }), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@emploi_du_temps_bp.route('/horaires/<int:id>', methods=['PUT'])
def update_horaire(id):
    """Mettre à jour un horaire"""
    try:
        data = request.get_json()
        horaire = HoraireService.update(id, data)
        if horaire:
            return jsonify({
                'success': True,
                'data': horaire.to_dict(),
                'message': 'Horaire mis à jour'
            }), 200
        return jsonify({'success': False, 'error': 'Horaire non trouvé'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@emploi_du_temps_bp.route('/horaires/<int:id>', methods=['DELETE'])
def delete_horaire(id):
    """Supprimer un horaire"""
    try:
        if HoraireService.delete(id):
            return jsonify({'success': True, 'message': 'Horaire supprimé'}), 200
        return jsonify({'success': False, 'error': 'Horaire non trouvé'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@emploi_du_temps_bp.route('/horaires/batch-delete', methods=['DELETE'])
def batch_delete_horaires():
    """Supprimer plusieurs horaires selon les filtres"""
    try:
        data = request.get_json() or {}
        
        count = HoraireService.delete_by_filters(
            classe_id=data.get('classe_id'),
            annee_scolaire_id=data.get('annee_scolaire_id'),
            jour_semaine=data.get('jour_semaine')
        )
        return jsonify({
            'success': True,
            'message': f'{count} horaire(s) supprimé(s)',
            'count': count
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@emploi_du_temps_bp.route('/horaires/verifier-collision', methods=['POST'])
def verifier_collision():
    """Vérifier s'il y a une collision avant création"""
    try:
        data = request.get_json()
        
        required_fields = ['matiere_classe_id', 'jour_semaine', 'creneau_id', 'annee_scolaire_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400
        
        has_collision, message = HoraireService.verifier_collision(
            data['matiere_classe_id'],
            data['jour_semaine'],
            data['creneau_id'],
            data['annee_scolaire_id']
        )
        
        return jsonify({
            'success': True,
            'has_collision': has_collision,
            'message': message
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500