from flask import Blueprint, request, jsonify
from services.evaluation_service import NoteService, DisciplineService
from datetime import datetime

evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/api/evaluation')


# ==================== NOTES ====================

@evaluation_bp.route('/notes', methods=['GET'])
def get_all_notes():
    """Récupérer toutes les notes."""
    try:
        notes = NoteService.get_all()
        return jsonify({
            'success': True,
            'data': [note.to_dict() for note in notes],
            'count': len(notes)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@evaluation_bp.route('/notes/<int:note_id>', methods=['GET'])
def get_note_by_id(note_id):
    """Récupérer une note par son ID."""
    try:
        note = NoteService.get_by_id(note_id)
        if note:
            return jsonify({'success': True, 'data': note.to_dict()}), 200
        return jsonify({'success': False, 'error': 'Note non trouvée'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@evaluation_bp.route('/notes/inscription/<int:inscription_id>', methods=['GET'])
def get_notes_by_inscription(inscription_id):
    """Récupérer toutes les notes d'un élève (inscription)."""
    try:
        notes = NoteService.get_by_inscription(inscription_id)
        return jsonify({
            'success': True,
            'data': [note.to_dict() for note in notes],
            'count': len(notes)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@evaluation_bp.route('/notes/sequence/<int:sequence_id>', methods=['GET'])
def get_notes_by_sequence(sequence_id):
    """Récupérer toutes les notes d'une séquence."""
    try:
        notes = NoteService.get_by_sequence(sequence_id)
        return jsonify({
            'success': True,
            'data': [note.to_dict() for note in notes],
            'count': len(notes)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@evaluation_bp.route('/notes/inscription/<int:inscription_id>/matiere/<int:matiere_classe_id>/sequence/<int:sequence_id>', methods=['GET'])
def get_note_by_inscription_matiere_sequence(inscription_id, matiere_classe_id, sequence_id):
    """Récupérer une note spécifique par inscription, matière et séquence."""
    try:
        note = NoteService.get_by_inscription_matiere_sequence(
            inscription_id, matiere_classe_id, sequence_id
        )
        if note:
            return jsonify({'success': True, 'data': note.to_dict()}), 200
        return jsonify({'success': False, 'error': 'Note non trouvée'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@evaluation_bp.route('/notes', methods=['POST'])
def create_note():
    """Créer une nouvelle note."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Données requises'}), 400
        
        required_fields = ['inscription_id', 'matiere_classe_id', 'sequence_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400

        # 'valeur' est requis sauf si l'élève est marqué absent (elle vaudra 0 par défaut)
        if not data.get('absent') and 'valeur' not in data:
            return jsonify({'success': False, 'error': 'Champ valeur requis (sauf si absent=true)'}), 400

        note = NoteService.create(data)
        return jsonify({
            'success': True,
            'data': note.to_dict(),
            'message': 'Note créée avec succès'
        }), 201
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@evaluation_bp.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Mettre à jour une note existante."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Données requises'}), 400
        
        note = NoteService.update(note_id, data)
        if note:
            return jsonify({
                'success': True,
                'data': note.to_dict(),
                'message': 'Note mise à jour avec succès'
            }), 200
        
        return jsonify({'success': False, 'error': 'Note non trouvée'}), 404
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@evaluation_bp.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Supprimer une note."""
    try:
        if NoteService.delete(note_id):
            return jsonify({'success': True, 'message': 'Note supprimée avec succès'}), 200
        return jsonify({'success': False, 'error': 'Note non trouvée'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@evaluation_bp.route('/notes/inscription/<int:inscription_id>/matiere/<int:matiere_classe_id>/moyenne', methods=['GET'])
def get_moyenne_matiere(inscription_id, matiere_classe_id):
    """Calculer la moyenne d'un élève pour une matière donnée."""
    try:
        moyenne = NoteService.calculate_moyenne_matiere(inscription_id, matiere_classe_id)
        
        if moyenne is not None:
            return jsonify({
                'success': True,
                'data': {
                    'inscription_id': inscription_id,
                    'matiere_classe_id': matiere_classe_id,
                    'moyenne': moyenne
                }
            }), 200
        
        return jsonify({
            'success': False,
            'error': 'Aucune note trouvée pour calculer la moyenne'
        }), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== DISCIPLINE ====================

@evaluation_bp.route('/discipline', methods=['GET'])
def get_all_discipline():
    """Récupérer tous les enregistrements de discipline."""
    try:
        disciplines = DisciplineService.get_all()
        return jsonify({
            'success': True,
            'data': [d.to_dict() for d in disciplines],
            'count': len(disciplines)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@evaluation_bp.route('/discipline/<int:discipline_id>', methods=['GET'])
def get_discipline_by_id(discipline_id):
    """Récupérer un enregistrement de discipline par son ID."""
    try:
        discipline = DisciplineService.get_by_id(discipline_id)
        if discipline:
            return jsonify({'success': True, 'data': discipline.to_dict()}), 200
        return jsonify({'success': False, 'error': 'Enregistrement de discipline non trouvé'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@evaluation_bp.route('/discipline/inscription/<int:inscription_id>', methods=['GET'])
def get_discipline_by_inscription(inscription_id):
    """Récupérer toutes les données de discipline d'un élève."""
    try:
        disciplines = DisciplineService.get_by_inscription(inscription_id)
        return jsonify({
            'success': True,
            'data': [d.to_dict() for d in disciplines],
            'count': len(disciplines)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@evaluation_bp.route('/discipline/sequence/<int:sequence_id>', methods=['GET'])
def get_discipline_by_sequence(sequence_id):
    """Récupérer toutes les données de discipline d'une séquence."""
    try:
        disciplines = DisciplineService.get_by_sequence(sequence_id)
        return jsonify({
            'success': True,
            'data': [d.to_dict() for d in disciplines],
            'count': len(disciplines)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@evaluation_bp.route('/discipline/inscription/<int:inscription_id>/sequence/<int:sequence_id>', methods=['GET'])
def get_discipline_by_inscription_sequence(inscription_id, sequence_id):
    """Récupérer la discipline pour un élève et une séquence donnés."""
    try:
        discipline = DisciplineService.get_by_inscription_sequence(inscription_id, sequence_id)
        if discipline:
            return jsonify({'success': True, 'data': discipline.to_dict()}), 200
        return jsonify({'success': False, 'error': 'Enregistrement de discipline non trouvé'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@evaluation_bp.route('/discipline', methods=['POST'])
def create_discipline():
    """Créer un nouvel enregistrement de discipline."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Données requises'}), 400
        
        required_fields = ['inscription_id', 'sequence_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400
        
        discipline = DisciplineService.create(data)
        return jsonify({
            'success': True,
            'data': discipline.to_dict(),
            'message': 'Enregistrement de discipline créé avec succès'
        }), 201
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@evaluation_bp.route('/discipline/<int:discipline_id>', methods=['PUT'])
def update_discipline(discipline_id):
    """Mettre à jour un enregistrement de discipline."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Données requises'}), 400
        
        discipline = DisciplineService.update(discipline_id, data)
        if discipline:
            return jsonify({
                'success': True,
                'data': discipline.to_dict(),
                'message': 'Discipline mise à jour avec succès'
            }), 200
        
        return jsonify({'success': False, 'error': 'Enregistrement de discipline non trouvé'}), 404
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@evaluation_bp.route('/discipline/<int:discipline_id>', methods=['DELETE'])
def delete_discipline(discipline_id):
    """Supprimer un enregistrement de discipline."""
    try:
        if DisciplineService.delete(discipline_id):
            return jsonify({'success': True, 'message': 'Discipline supprimée avec succès'}), 200
        return jsonify({'success': False, 'error': 'Enregistrement de discipline non trouvé'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@evaluation_bp.route('/discipline/inscription/<int:inscription_id>/trimestre/<int:trimestre_id>/aggregation', methods=['GET'])
def get_discipline_aggregation_trimestre(inscription_id, trimestre_id):
    """Obtenir l'agrégation de la discipline pour un trimestre."""
    try:
        aggregation = DisciplineService.get_aggregation_by_trimestre(
            inscription_id, trimestre_id
        )
        return jsonify({
            'success': True,
            'data': aggregation
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@evaluation_bp.route('/discipline/inscription/<int:inscription_id>/annee/<int:annee_scolaire_id>/aggregation', methods=['GET'])
def get_discipline_aggregation_annee(inscription_id, annee_scolaire_id):
    """Obtenir l'agrégation de la discipline pour une année scolaire."""
    try:
        aggregation = DisciplineService.get_aggregation_by_annee(
            inscription_id, annee_scolaire_id
        )
        return jsonify({
            'success': True,
            'data': aggregation
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500