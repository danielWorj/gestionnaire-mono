from flask import Blueprint, request, jsonify
from services.pedagogie_service import (
    EnseignantService, GroupeMatiereService, MatiereService,
    TitulaireClasseService, MatiereClasseService
)
from datetime import datetime

pedagogie_bp = Blueprint('pedagogie', __name__, url_prefix='/api/pedagogie')

# NOTE: les routes pour AnneeScolaire et Classe ont été retirées de ce blueprint.
# Elles sont déjà exposées par structure_bp sous /api/structure/annees-scolaires
# et /api/structure/classes (via structure_service.py), qui est la seule source
# de vérité pour ces deux modèles.


# ==================== ENSEIGNANT ====================

@pedagogie_bp.route('/enseignants', methods=['GET'])
def get_all_enseignants():
    """Récupérer tous les enseignants"""
    try:
        enseignants = EnseignantService.get_all()
        return jsonify({
            'success': True,
            'data': [ens.to_dict() for ens in enseignants],
            'count': len(enseignants)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/enseignants/<int:id>', methods=['GET'])
def get_enseignant_by_id(id):
    """Récupérer un enseignant par ID"""
    try:
        enseignant = EnseignantService.get_by_id(id)
        if enseignant:
            return jsonify({'success': True, 'data': enseignant.to_dict()}), 200
        return jsonify({'success': False, 'error': 'Enseignant non trouvé'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/enseignants', methods=['POST'])
def create_enseignant():
    """Créer un nouvel enseignant"""
    try:
        data = request.get_json()

        required_fields = ['nom', 'prenom', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400

        enseignant = EnseignantService.create(data)
        return jsonify({'success': True, 'data': enseignant.to_dict(), 'message': 'Enseignant créé'}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/enseignants/<int:id>', methods=['PUT'])
def update_enseignant(id):
    """Mettre à jour un enseignant"""
    try:
        data = request.get_json()
        enseignant = EnseignantService.update(id, data)
        if enseignant:
            return jsonify({'success': True, 'data': enseignant.to_dict(), 'message': 'Enseignant mis à jour'}), 200
        return jsonify({'success': False, 'error': 'Enseignant non trouvé'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/enseignants/<int:id>', methods=['DELETE'])
def delete_enseignant(id):
    """Supprimer un enseignant"""
    try:
        if EnseignantService.delete(id):
            return jsonify({'success': True, 'message': 'Enseignant supprimé'}), 200
        return jsonify({'success': False, 'error': 'Enseignant non trouvé'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== GROUPE MATIÈRE ====================

@pedagogie_bp.route('/groupes-matiere', methods=['GET'])
def get_all_groupes():
    """Récupérer tous les groupes de matières"""
    try:
        groupes = GroupeMatiereService.get_all()
        return jsonify({
            'success': True,
            'data': [groupe.to_dict() for groupe in groupes],
            'count': len(groupes)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/groupes-matiere/<int:id>', methods=['GET'])
def get_groupe_by_id(id):
    """Récupérer un groupe de matière par ID"""
    try:
        groupe = GroupeMatiereService.get_by_id(id)
        if groupe:
            return jsonify({'success': True, 'data': groupe.to_dict()}), 200
        return jsonify({'success': False, 'error': 'Groupe non trouvé'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/groupes-matiere', methods=['POST'])
def create_groupe():
    """Créer un nouveau groupe de matière"""
    try:
        data = request.get_json()

        required_fields = ['libelle']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400

        groupe = GroupeMatiereService.create(data)
        return jsonify({'success': True, 'data': groupe.to_dict(), 'message': 'Groupe créé'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/groupes-matiere/<int:id>', methods=['PUT'])
def update_groupe(id):
    """Mettre à jour un groupe de matière"""
    try:
        data = request.get_json()
        groupe = GroupeMatiereService.update(id, data)
        if groupe:
            return jsonify({'success': True, 'data': groupe.to_dict(), 'message': 'Groupe mis à jour'}), 200
        return jsonify({'success': False, 'error': 'Groupe non trouvé'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/groupes-matiere/<int:id>', methods=['DELETE'])
def delete_groupe(id):
    """Supprimer un groupe de matière"""
    try:
        if GroupeMatiereService.delete(id):
            return jsonify({'success': True, 'message': 'Groupe supprimé'}), 200
        return jsonify({'success': False, 'error': 'Groupe non trouvé'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== MATIÈRE ====================

@pedagogie_bp.route('/matieres', methods=['GET'])
def get_all_matieres():
    """Récupérer toutes les matières"""
    try:
        matieres = MatiereService.get_all()
        return jsonify({
            'success': True,
            'data': [matiere.to_dict() for matiere in matieres],
            'count': len(matieres)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/matieres/<int:id>', methods=['GET'])
def get_matiere_by_id(id):
    """Récupérer une matière par ID"""
    try:
        matiere = MatiereService.get_by_id(id)
        if matiere:
            return jsonify({'success': True, 'data': matiere.to_dict()}), 200
        return jsonify({'success': False, 'error': 'Matière non trouvée'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/groupes-matiere/<int:groupe_id>/matieres', methods=['GET'])
def get_matieres_by_groupe(groupe_id):
    """Récupérer les matières d'un groupe"""
    try:
        matieres = MatiereService.get_by_groupe(groupe_id)
        return jsonify({
            'success': True,
            'data': [matiere.to_dict() for matiere in matieres],
            'count': len(matieres)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/matieres', methods=['POST'])
def create_matiere():
    """Créer une nouvelle matière"""
    try:
        data = request.get_json()

        required_fields = ['libelle', 'groupe_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400

        matiere = MatiereService.create(data)
        return jsonify({'success': True, 'data': matiere.to_dict(), 'message': 'Matière créée'}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/matieres/<int:id>', methods=['PUT'])
def update_matiere(id):
    """Mettre à jour une matière"""
    try:
        data = request.get_json()
        matiere = MatiereService.update(id, data)
        if matiere:
            return jsonify({'success': True, 'data': matiere.to_dict(), 'message': 'Matière mise à jour'}), 200
        return jsonify({'success': False, 'error': 'Matière non trouvée'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/matieres/<int:id>', methods=['DELETE'])
def delete_matiere(id):
    """Supprimer une matière"""
    try:
        if MatiereService.delete(id):
            return jsonify({'success': True, 'message': 'Matière supprimée'}), 200
        return jsonify({'success': False, 'error': 'Matière non trouvée'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== TITULAIRE CLASSE ====================

@pedagogie_bp.route('/titulaires-classe', methods=['GET'])
def get_all_titulaires():
    """Récupérer tous les titulaires de classe"""
    try:
        titulaires = TitulaireClasseService.get_all()
        return jsonify({
            'success': True,
            'data': [titulaire.to_dict() for titulaire in titulaires],
            'count': len(titulaires)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/titulaires-classe/<int:id>', methods=['GET'])
def get_titulaire_by_id(id):
    """Récupérer un titulaire par ID"""
    try:
        titulaire = TitulaireClasseService.get_by_id(id)
        if titulaire:
            return jsonify({'success': True, 'data': titulaire.to_dict()}), 200
        return jsonify({'success': False, 'error': 'Titulaire non trouvé'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/titulaires-classe', methods=['POST'])
def create_titulaire():
    """Affecter un titulaire à une classe"""
    try:
        data = request.get_json()

        required_fields = ['classe_id', 'enseignant_id', 'annee_scolaire_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400

        titulaire = TitulaireClasseService.create(data)
        return jsonify({'success': True, 'data': titulaire.to_dict(), 'message': 'Titulaire affecté'}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/titulaires-classe/<int:id>', methods=['PUT'])
def update_titulaire(id):
    """Mettre à jour un titulaire"""
    try:
        data = request.get_json()
        titulaire = TitulaireClasseService.update(id, data)
        if titulaire:
            return jsonify({'success': True, 'data': titulaire.to_dict(), 'message': 'Titulaire mis à jour'}), 200
        return jsonify({'success': False, 'error': 'Titulaire non trouvé'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/titulaires-classe/<int:id>', methods=['DELETE'])
def delete_titulaire(id):
    """Supprimer un titulaire"""
    try:
        if TitulaireClasseService.delete(id):
            return jsonify({'success': True, 'message': 'Titulaire supprimé'}), 200
        return jsonify({'success': False, 'error': 'Titulaire non trouvé'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== MATIÈRE CLASSE ====================

@pedagogie_bp.route('/matieres-classe', methods=['GET'])
def get_all_matieres_classe():
    """Récupérer toutes les affectations matières-classes"""
    try:
        matieres_classe = MatiereClasseService.get_all()
        return jsonify({
            'success': True,
            'data': [mc.to_dict() for mc in matieres_classe],
            'count': len(matieres_classe)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/matieres-classe/<int:id>', methods=['GET'])
def get_matiere_classe_by_id(id):
    """Récupérer une affectation matière-classe par ID"""
    try:
        matiere_classe = MatiereClasseService.get_by_id(id)
        if matiere_classe:
            return jsonify({'success': True, 'data': matiere_classe.to_dict()}), 200
        return jsonify({'success': False, 'error': 'Affectation non trouvée'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/classes/<int:classe_id>/matieres', methods=['GET'])
def get_matieres_by_classe(classe_id):
    """Récupérer les matières d'une classe"""
    try:
        matieres_classe = MatiereClasseService.get_by_classe(classe_id)
        return jsonify({
            'success': True,
            'data': [mc.to_dict() for mc in matieres_classe],
            'count': len(matieres_classe)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/matieres-classe', methods=['POST'])
def create_matiere_classe():
    """Affecter une matière à une classe"""
    try:
        data = request.get_json()

        required_fields = ['classe_id', 'matiere_id', 'enseignant_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400

        matiere_classe = MatiereClasseService.create(data)
        return jsonify({'success': True, 'data': matiere_classe.to_dict(), 'message': 'Matière affectée à la classe'}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/matieres-classe/<int:id>', methods=['PUT'])
def update_matiere_classe(id):
    """Mettre à jour une affectation matière-classe"""
    try:
        data = request.get_json()
        matiere_classe = MatiereClasseService.update(id, data)
        if matiere_classe:
            return jsonify({'success': True, 'data': matiere_classe.to_dict(), 'message': 'Affectation mise à jour'}), 200
        return jsonify({'success': False, 'error': 'Affectation non trouvée'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pedagogie_bp.route('/matieres-classe/<int:id>', methods=['DELETE'])
def delete_matiere_classe(id):
    """Supprimer une affectation matière-classe"""
    try:
        if MatiereClasseService.delete(id):
            return jsonify({'success': True, 'message': 'Affectation supprimée'}), 200
        return jsonify({'success': False, 'error': 'Affectation non trouvée'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500