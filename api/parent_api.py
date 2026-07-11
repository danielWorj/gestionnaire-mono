from flask import Blueprint, request, jsonify
from services.parent_service import ParentService

parent_bp = Blueprint('parent', __name__, url_prefix='/api/parents')


@parent_bp.route('', methods=['GET'])
def get_all_parents():
    """Récupérer tous les parents"""
    try:
        parents = ParentService.get_all()
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in parents],
            'count': len(parents)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@parent_bp.route('/<int:id>', methods=['GET'])
def get_parent_by_id(id):
    """Récupérer un parent par ID (avec la liste de ses élèves)"""
    try:
        parent = ParentService.get_by_id(id)
        if parent:
            return jsonify({'success': True, 'data': parent.to_dict(with_eleves=True)}), 200
        return jsonify({'success': False, 'error': 'Parent non trouvé'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@parent_bp.route('', methods=['POST'])
def create_parent():
    """Créer un nouveau parent"""
    try:
        data = request.get_json()

        required_fields = ['nom', 'prenom']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400

        parent = ParentService.create(data)
        return jsonify({'success': True, 'data': parent.to_dict(), 'message': 'Parent créé'}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@parent_bp.route('/<int:id>', methods=['PUT'])
def update_parent(id):
    """Mettre à jour un parent"""
    try:
        data = request.get_json()
        parent = ParentService.update(id, data)
        if parent:
            return jsonify({'success': True, 'data': parent.to_dict(), 'message': 'Parent mis à jour'}), 200
        return jsonify({'success': False, 'error': 'Parent non trouvé'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@parent_bp.route('/<int:id>', methods=['DELETE'])
def delete_parent(id):
    """Supprimer un parent"""
    try:
        if ParentService.delete(id):
            return jsonify({'success': True, 'message': 'Parent supprimé'}), 200
        return jsonify({'success': False, 'error': 'Parent non trouvé'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500