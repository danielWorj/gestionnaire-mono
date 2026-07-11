from flask import Blueprint, request, jsonify
from services.structure_service import (
    EtablissementService, AnneeScolaireService, TrimestreService,
    SequenceService, CycleService, ClasseService
)
from datetime import datetime

structure_bp = Blueprint('structure', __name__, url_prefix='/api/structure')


# ==================== ÉTABLISSEMENT ====================

@structure_bp.route('/etablissement', methods=['GET'])
def get_etablissement():
    """Récupère les informations de l'établissement"""
    try:
        etablissement = EtablissementService.get_etablissement()
        if not etablissement:
            return jsonify({'success': False, 'error': 'Établissement non configuré'}), 404
        return jsonify({'success': True, 'data': etablissement.to_dict()}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/etablissement', methods=['POST'])
def create_etablissement():
    """Crée l'établissement (une seule fois)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Données requises'}), 400
        
        etablissement = EtablissementService.create_etablissement(data)
        return jsonify({'success': True, 'data': etablissement.to_dict(), 'message': 'Établissement créé'}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 409
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/etablissement', methods=['PUT'])
def update_etablissement():
    """Met à jour l'établissement"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Données requises'}), 400
        
        etablissement = EtablissementService.update_etablissement(data)
        return jsonify({'success': True, 'data': etablissement.to_dict(), 'message': 'Établissement mis à jour'}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== ANNÉES SCOLAIRES ====================

@structure_bp.route('/annees-scolaires', methods=['GET'])
def get_annees_scolaires():
    """Récupère toutes les années scolaires"""
    try:
        annees = AnneeScolaireService.get_all()
        return jsonify({'success': True, 'data': [a.to_dict() for a in annees]}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/annees-scolaires/active', methods=['GET'])
def get_annee_active():
    """Récupère l'année scolaire active"""
    try:
        annee = AnneeScolaireService.get_active()
        if not annee:
            return jsonify({'success': False, 'error': 'Aucune année active'}), 404
        return jsonify({'success': True, 'data': annee.to_dict()}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/annees-scolaires/<int:id>', methods=['GET'])
def get_annee_scolaire(id):
    """Récupère une année scolaire par ID"""
    try:
        annee = AnneeScolaireService.get_by_id(id)
        if not annee:
            return jsonify({'success': False, 'error': 'Année non trouvée'}), 404
        return jsonify({'success': True, 'data': annee.to_dict()}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/annees-scolaires', methods=['POST'])
def create_annee_scolaire():
    """Crée une nouvelle année scolaire"""
    try:
        data = request.get_json()
        if not data or 'libelle' not in data:
            return jsonify({'success': False, 'error': 'Libelle requis'}), 400
        
        # Parser les dates si présentes
        if 'date_debut' in data:
            data['date_debut'] = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
        if 'date_fin' in data:
            data['date_fin'] = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
        
        annee = AnneeScolaireService.create(data)
        return jsonify({'success': True, 'data': annee.to_dict(), 'message': 'Année scolaire créée'}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 409
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/annees-scolaires/<int:id>', methods=['PUT'])
def update_annee_scolaire(id):
    """Met à jour une année scolaire"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Données requises'}), 400
        
        # Parser les dates si présentes
        if 'date_debut' in data:
            data['date_debut'] = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
        if 'date_fin' in data:
            data['date_fin'] = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
        
        annee = AnneeScolaireService.update(id, data)
        return jsonify({'success': True, 'data': annee.to_dict(), 'message': 'Année scolaire mise à jour'}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/annees-scolaires/<int:id>', methods=['DELETE'])
def delete_annee_scolaire(id):
    """Supprime une année scolaire"""
    try:
        AnneeScolaireService.delete(id)
        return jsonify({'success': True, 'message': 'Année scolaire supprimée'}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/annees-scolaires/<int:id>/activer', methods=['POST'])
def activer_annee_scolaire(id):
    """Active une année scolaire"""
    try:
        annee = AnneeScolaireService.set_active(id)
        if not annee:
            return jsonify({'success': False, 'error': 'Année non trouvée'}), 404
        return jsonify({'success': True, 'data': annee.to_dict(), 'message': 'Année scolaire activée'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== TRIMESTRES ====================

@structure_bp.route('/annees-scolaires/<int:annee_id>/trimestres', methods=['GET'])
def get_trimestres_by_annee(annee_id):
    """Récupère les trimestres d'une année"""
    try:
        trimestres = TrimestreService.get_by_annee(annee_id)
        return jsonify({'success': True, 'data': [t.to_dict() for t in trimestres]}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/trimestres/<int:id>', methods=['GET'])
def get_trimestre(id):
    """Récupère un trimestre par ID"""
    try:
        trimestre = TrimestreService.get_by_id(id)
        if not trimestre:
            return jsonify({'success': False, 'error': 'Trimestre non trouvé'}), 404
        return jsonify({'success': True, 'data': trimestre.to_dict()}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/trimestres', methods=['POST'])
def create_trimestre():
    """Crée un nouveau trimestre"""
    try:
        data = request.get_json()
        if not data or 'annee_scolaire_id' not in data or 'libelle' not in data or 'numero' not in data:
            return jsonify({'success': False, 'error': 'Champs requis manquants'}), 400
        
        # Parser les dates si présentes
        if 'date_debut' in data:
            data['date_debut'] = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
        if 'date_fin' in data:
            data['date_fin'] = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
        
        trimestre = TrimestreService.create(data)
        return jsonify({'success': True, 'data': trimestre.to_dict(), 'message': 'Trimestre créé'}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 409
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/trimestres/<int:id>', methods=['PUT'])
def update_trimestre(id):
    """Met à jour un trimestre"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Données requises'}), 400
        
        # Parser les dates si présentes
        if 'date_debut' in data:
            data['date_debut'] = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
        if 'date_fin' in data:
            data['date_fin'] = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
        
        trimestre = TrimestreService.update(id, data)
        return jsonify({'success': True, 'data': trimestre.to_dict(), 'message': 'Trimestre mis à jour'}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/trimestres/<int:id>', methods=['DELETE'])
def delete_trimestre(id):
    """Supprime un trimestre"""
    try:
        TrimestreService.delete(id)
        return jsonify({'success': True, 'message': 'Trimestre supprimé'}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== SÉQUENCES ====================

@structure_bp.route('/trimestres/<int:trimestre_id>/sequences', methods=['GET'])
def get_sequences_by_trimestre(trimestre_id):
    """Récupère les séquences d'un trimestre"""
    try:
        sequences = SequenceService.get_by_trimestre(trimestre_id)
        return jsonify({'success': True, 'data': [s.to_dict() for s in sequences]}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/sequences/<int:id>', methods=['GET'])
def get_sequence(id):
    """Récupère une séquence par ID"""
    try:
        sequence = SequenceService.get_by_id(id)
        if not sequence:
            return jsonify({'success': False, 'error': 'Séquence non trouvée'}), 404
        return jsonify({'success': True, 'data': sequence.to_dict()}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/sequences', methods=['POST'])
def create_sequence():
    """Crée une nouvelle séquence"""
    try:
        data = request.get_json()
        if not data or 'trimestre_id' not in data or 'libelle' not in data or 'numero' not in data:
            return jsonify({'success': False, 'error': 'Champs requis manquants'}), 400
        
        # Parser les dates si présentes
        if 'date_debut' in data:
            data['date_debut'] = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
        if 'date_fin' in data:
            data['date_fin'] = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
        
        sequence = SequenceService.create(data)
        return jsonify({'success': True, 'data': sequence.to_dict(), 'message': 'Séquence créée'}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 409
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/sequences/<int:id>', methods=['PUT'])
def update_sequence(id):
    """Met à jour une séquence"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Données requises'}), 400
        
        # Parser les dates si présentes
        if 'date_debut' in data:
            data['date_debut'] = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
        if 'date_fin' in data:
            data['date_fin'] = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
        
        sequence = SequenceService.update(id, data)
        return jsonify({'success': True, 'data': sequence.to_dict(), 'message': 'Séquence mise à jour'}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/sequences/<int:id>', methods=['DELETE'])
def delete_sequence(id):
    """Supprime une séquence"""
    try:
        SequenceService.delete(id)
        return jsonify({'success': True, 'message': 'Séquence supprimée'}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== CYCLES ====================

@structure_bp.route('/cycles', methods=['GET'])
def get_cycles():
    """Récupère tous les cycles"""
    try:
        cycles = CycleService.get_all()
        return jsonify({'success': True, 'data': [c.to_dict() for c in cycles]}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/cycles/<int:id>', methods=['GET'])
def get_cycle(id):
    """Récupère un cycle par ID"""
    try:
        cycle = CycleService.get_by_id(id)
        if not cycle:
            return jsonify({'success': False, 'error': 'Cycle non trouvé'}), 404
        return jsonify({'success': True, 'data': cycle.to_dict()}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/cycles', methods=['POST'])
def create_cycle():
    """Crée un nouveau cycle"""
    try:
        data = request.get_json()
        if not data or 'ordre' not in data or 'libelle' not in data:
            return jsonify({'success': False, 'error': 'Champs requis manquants'}), 400
        
        cycle = CycleService.create(data)
        return jsonify({'success': True, 'data': cycle.to_dict(), 'message': 'Cycle créé'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/cycles/<int:id>', methods=['PUT'])
def update_cycle(id):
    """Met à jour un cycle"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Données requises'}), 400
        
        cycle = CycleService.update(id, data)
        return jsonify({'success': True, 'data': cycle.to_dict(), 'message': 'Cycle mis à jour'}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/cycles/<int:id>', methods=['DELETE'])
def delete_cycle(id):
    """Supprime un cycle"""
    try:
        CycleService.delete(id)
        return jsonify({'success': True, 'message': 'Cycle supprimé'}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== CLASSES ====================

@structure_bp.route('/classes', methods=['GET'])
def get_classes():
    """Récupère toutes les classes"""
    try:
        classes = ClasseService.get_all()
        return jsonify({'success': True, 'data': [c.to_dict() for c in classes]}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/cycles/<int:cycle_id>/classes', methods=['GET'])
def get_classes_by_cycle(cycle_id):
    """Récupère les classes d'un cycle"""
    try:
        classes = ClasseService.get_by_cycle(cycle_id)
        return jsonify({'success': True, 'data': [c.to_dict() for c in classes]}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/classes/<int:id>', methods=['GET'])
def get_classe(id):
    """Récupère une classe par ID"""
    try:
        classe = ClasseService.get_by_id(id)
        if not classe:
            return jsonify({'success': False, 'error': 'Classe non trouvée'}), 404
        return jsonify({'success': True, 'data': classe.to_dict()}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/classes', methods=['POST'])
def create_classe():
    """Crée une nouvelle classe"""
    try:
        data = request.get_json()
        if not data or 'libelle' not in data or 'cycle_id' not in data:
            return jsonify({'success': False, 'error': 'Champs requis manquants'}), 400
        
        classe = ClasseService.create(data)
        return jsonify({'success': True, 'data': classe.to_dict(), 'message': 'Classe créée'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/classes/<int:id>', methods=['PUT'])
def update_classe(id):
    """Met à jour une classe"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Données requises'}), 400
        
        classe = ClasseService.update(id, data)
        return jsonify({'success': True, 'data': classe.to_dict(), 'message': 'Classe mise à jour'}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@structure_bp.route('/classes/<int:id>', methods=['DELETE'])
def delete_classe(id):
    """Supprime une classe"""
    try:
        ClasseService.delete(id)
        return jsonify({'success': True, 'message': 'Classe supprimée'}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500