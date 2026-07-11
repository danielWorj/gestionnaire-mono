from flask import Blueprint, request, jsonify, send_from_directory
from services.inscription_service import EleveService, InscriptionService, BASE_DIR

inscription_bp = Blueprint('inscription', __name__, url_prefix='/api/inscription')


# ==================== ELEVE ====================

@inscription_bp.route('/eleves', methods=['GET'])
def get_all_eleves():
    """Récupérer tous les élèves"""
    try:
        eleves = EleveService.get_all()
        return jsonify({
            'success': True,
            'data': [eleve.to_dict() for eleve in eleves],
            'count': len(eleves)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@inscription_bp.route('/eleves/<int:id>', methods=['GET'])
def get_eleve_by_id(id):
    """Récupérer un élève par ID"""
    try:
        eleve = EleveService.get_by_id(id)
        if eleve:
            return jsonify({'success': True, 'data': eleve.to_dict()}), 200
        return jsonify({'success': False, 'error': 'Élève non trouvé'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@inscription_bp.route('/eleves/matricule/<string:matricule>', methods=['GET'])
def get_eleve_by_matricule(matricule):
    """Récupérer un élève par matricule"""
    try:
        eleve = EleveService.get_by_matricule(matricule)
        if eleve:
            return jsonify({'success': True, 'data': eleve.to_dict()}), 200
        return jsonify({'success': False, 'error': 'Élève non trouvé'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@inscription_bp.route('/eleves', methods=['POST'])
def create_eleve():
    """
    Créer un nouvel élève.
    Envoi en multipart/form-data (et non en JSON) car une photo peut être jointe.

    Champs texte (form fields):
      - matricule, nom, prenom (requis)
      - date_naissance, lieu_naissance, sexe, adresse (optionnels)
      - parent_id (parent existant) OU
        parent_nom + parent_prenom (+ parent_telephone, parent_email,
        parent_adresse, parent_profession) pour créer un nouveau parent
    Fichier:
      - photo (optionnel): image du/de la élève, sauvegardée dans storage/eleves/
    """
    try:
        data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
        photo_file = request.files.get('photo')

        required_fields = ['matricule', 'nom', 'prenom']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400

        eleve = EleveService.create(data, photo_file=photo_file)
        return jsonify({'success': True, 'data': eleve.to_dict(), 'message': 'Élève créé'}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@inscription_bp.route('/eleves/<int:id>', methods=['PUT'])
def update_eleve(id):
    """Mettre à jour un élève (multipart/form-data si une nouvelle photo est envoyée, JSON sinon)"""
    try:
        data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
        photo_file = request.files.get('photo')

        eleve = EleveService.update(id, data, photo_file=photo_file)
        if eleve:
            return jsonify({'success': True, 'data': eleve.to_dict(), 'message': 'Élève mis à jour'}), 200
        return jsonify({'success': False, 'error': 'Élève non trouvé'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@inscription_bp.route('/eleves/<int:id>', methods=['DELETE'])
def delete_eleve(id):
    """Supprimer un élève (supprime aussi sa photo du disque)"""
    try:
        if EleveService.delete(id):
            return jsonify({'success': True, 'message': 'Élève supprimé'}), 200
        return jsonify({'success': False, 'error': 'Élève non trouvé'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@inscription_bp.route('/eleves/<int:id>/photo', methods=['GET'])
def get_eleve_photo(id):
    """Servir le fichier photo d'un élève"""
    try:
        eleve = EleveService.get_by_id(id)
        if not eleve or not eleve.photo_url:
            return jsonify({'success': False, 'error': 'Photo non trouvée'}), 404
        # eleve.photo_url = 'storage/eleves/xxxx.jpg'
        return send_from_directory(str(BASE_DIR / 'storage' / 'eleves'), eleve.photo_url.split('/')[-1])
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== INSCRIPTION ====================

@inscription_bp.route('/inscriptions', methods=['GET'])
def get_all_inscriptions():
    """Récupérer toutes les inscriptions"""
    try:
        inscriptions = InscriptionService.get_all()
        return jsonify({
            'success': True,
            'data': [inscription.to_dict() for inscription in inscriptions],
            'count': len(inscriptions)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@inscription_bp.route('/inscriptions/<int:id>', methods=['GET'])
def get_inscription_by_id(id):
    """Récupérer une inscription par ID"""
    try:
        inscription = InscriptionService.get_by_id(id)
        if inscription:
            return jsonify({'success': True, 'data': inscription.to_dict()}), 200
        return jsonify({'success': False, 'error': 'Inscription non trouvée'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@inscription_bp.route('/classes/<int:classe_id>/annees/<int:annee_scolaire_id>/inscriptions', methods=['GET'])
def get_inscriptions_by_classe_annee(classe_id, annee_scolaire_id):
    """Récupérer la liste des élèves inscrits dans une classe pour une année"""
    try:
        inscriptions = InscriptionService.get_by_classe_annee(classe_id, annee_scolaire_id)
        return jsonify({
            'success': True,
            'data': [inscription.to_dict() for inscription in inscriptions],
            'count': len(inscriptions)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@inscription_bp.route('/annees/<int:annee_scolaire_id>/inscriptions', methods=['GET'])
def get_inscriptions_by_annee(annee_scolaire_id):
    """Récupérer toutes les inscriptions d'une année scolaire"""
    try:
        inscriptions = InscriptionService.get_by_annee(annee_scolaire_id)
        return jsonify({
            'success': True,
            'data': [inscription.to_dict() for inscription in inscriptions],
            'count': len(inscriptions)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@inscription_bp.route('/eleves/<int:eleve_id>/historique', methods=['GET'])
def get_historique_eleve(eleve_id):
    """Récupérer l'historique des inscriptions d'un élève (toutes années)"""
    try:
        inscriptions = InscriptionService.get_historique_eleve(eleve_id)
        return jsonify({
            'success': True,
            'data': [inscription.to_dict() for inscription in inscriptions],
            'count': len(inscriptions)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@inscription_bp.route('/eleves/<int:eleve_id>/annees/<int:annee_scolaire_id>/inscription-active', methods=['GET'])
def get_inscription_active(eleve_id, annee_scolaire_id):
    """Récupérer l'inscription active d'un élève pour une année donnée"""
    try:
        inscription = InscriptionService.get_inscription_active(eleve_id, annee_scolaire_id)
        if inscription:
            return jsonify({'success': True, 'data': inscription.to_dict()}), 200
        return jsonify({'success': False, 'error': 'Aucune inscription trouvée'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@inscription_bp.route('/inscriptions', methods=['POST'])
def create_inscription():
    """Créer une nouvelle inscription"""
    try:
        data = request.get_json()

        required_fields = ['eleve_id', 'classe_id', 'annee_scolaire_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400

        inscription = InscriptionService.create(data)
        return jsonify({'success': True, 'data': inscription.to_dict(), 'message': 'Inscription créée'}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@inscription_bp.route('/inscriptions/<int:id>', methods=['PUT'])
def update_inscription(id):
    """Mettre à jour une inscription"""
    try:
        data = request.get_json()
        inscription = InscriptionService.update(id, data)
        if inscription:
            return jsonify({'success': True, 'data': inscription.to_dict(), 'message': 'Inscription mise à jour'}), 200
        return jsonify({'success': False, 'error': 'Inscription non trouvée'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@inscription_bp.route('/inscriptions/<int:id>/transfert', methods=['PUT'])
def transferer_classe(id):
    """Transférer un élève vers une autre classe (même année scolaire)"""
    try:
        data = request.get_json()

        if 'classe_id' not in data:
            return jsonify({'success': False, 'error': 'Champ classe_id requis'}), 400

        inscription = InscriptionService.transferer_classe(id, data['classe_id'])
        if inscription:
            return jsonify({'success': True, 'data': inscription.to_dict(), 'message': 'Élève transféré'}), 200
        return jsonify({'success': False, 'error': 'Inscription non trouvée'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@inscription_bp.route('/inscriptions/<int:id>', methods=['DELETE'])
def delete_inscription(id):
    """Supprimer une inscription"""
    try:
        if InscriptionService.delete(id):
            return jsonify({'success': True, 'message': 'Inscription supprimée'}), 200
        return jsonify({'success': False, 'error': 'Inscription non trouvée'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500