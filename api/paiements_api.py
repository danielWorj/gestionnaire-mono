from flask import Blueprint, request, jsonify
from services.paiements_service import TranchePaiementService, PaiementService

paiements_bp = Blueprint('paiements', __name__, url_prefix='/api/paiements')


# ==================== TRANCHE DE PAIEMENT ====================

@paiements_bp.route('/tranches', methods=['GET'])
def get_all_tranches():
    """Récupérer toutes les tranches de paiement"""
    try:
        tranches = TranchePaiementService.get_all()
        return jsonify({
            'success': True,
            'data': [t.to_dict() for t in tranches],
            'count': len(tranches)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@paiements_bp.route('/tranches/<int:id>', methods=['GET'])
def get_tranche_by_id(id):
    """Récupérer une tranche de paiement par ID"""
    try:
        tranche = TranchePaiementService.get_by_id(id)
        if tranche:
            return jsonify({'success': True, 'data': tranche.to_dict(with_annee=True)}), 200
        return jsonify({'success': False, 'error': 'Tranche de paiement non trouvée'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@paiements_bp.route('/annees/<int:annee_scolaire_id>/tranches', methods=['GET'])
def get_tranches_by_annee(annee_scolaire_id):
    """Récupérer les tranches de paiement d'une année scolaire"""
    try:
        tranches = TranchePaiementService.get_by_annee(annee_scolaire_id)
        return jsonify({
            'success': True,
            'data': [t.to_dict() for t in tranches],
            'count': len(tranches)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@paiements_bp.route('/classes/<int:classe_id>/tranches', methods=['GET'])
def get_tranches_by_classe(classe_id):
    """Récupérer les tranches de paiement d'une classe (toutes années confondues)"""
    try:
        tranches = TranchePaiementService.get_by_classe(classe_id)
        return jsonify({
            'success': True,
            'data': [t.to_dict() for t in tranches],
            'count': len(tranches)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@paiements_bp.route('/annees/<int:annee_scolaire_id>/classes/<int:classe_id>/tranches', methods=['GET'])
def get_tranches_by_annee_classe(annee_scolaire_id, classe_id):
    """Récupérer les tranches de paiement d'une classe pour une année scolaire donnée"""
    try:
        tranches = TranchePaiementService.get_by_annee_classe(annee_scolaire_id, classe_id)
        return jsonify({
            'success': True,
            'data': [t.to_dict() for t in tranches],
            'count': len(tranches)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@paiements_bp.route('/tranches/<int:id>/total-verse', methods=['GET'])
def get_total_verse_tranche(id):
    """Récupérer le total versé (toutes inscriptions) pour une tranche"""
    try:
        total = TranchePaiementService.get_total_verse(id)
        return jsonify({'success': True, 'data': {'tranche_id': id, 'total_verse': total}}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@paiements_bp.route('/tranches', methods=['POST'])
def create_tranche():
    """Créer une nouvelle tranche de paiement"""
    try:
        data = request.get_json()

        required_fields = ['annee_scolaire_id', 'classe_id', 'libelle', 'montant_attendu']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400

        tranche = TranchePaiementService.create(data)
        return jsonify({'success': True, 'data': tranche.to_dict(), 'message': 'Tranche de paiement créée'}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@paiements_bp.route('/tranches/<int:id>', methods=['PUT'])
def update_tranche(id):
    """Mettre à jour une tranche de paiement"""
    try:
        data = request.get_json()
        tranche = TranchePaiementService.update(id, data)
        if tranche:
            return jsonify({'success': True, 'data': tranche.to_dict(), 'message': 'Tranche de paiement mise à jour'}), 200
        return jsonify({'success': False, 'error': 'Tranche de paiement non trouvée'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@paiements_bp.route('/tranches/<int:id>', methods=['DELETE'])
def delete_tranche(id):
    """Supprimer une tranche de paiement"""
    try:
        if TranchePaiementService.delete(id):
            return jsonify({'success': True, 'message': 'Tranche de paiement supprimée'}), 200
        return jsonify({'success': False, 'error': 'Tranche de paiement non trouvée'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== PAIEMENT ====================

@paiements_bp.route('', methods=['GET'])
def get_all_paiements():
    """Récupérer tous les paiements"""
    try:
        paiements = PaiementService.get_all()
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in paiements],
            'count': len(paiements)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@paiements_bp.route('/<int:id>', methods=['GET'])
def get_paiement_by_id(id):
    """Récupérer un paiement par ID"""
    try:
        paiement = PaiementService.get_by_id(id)
        if paiement:
            return jsonify({'success': True, 'data': paiement.to_dict()}), 200
        return jsonify({'success': False, 'error': 'Paiement non trouvé'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@paiements_bp.route('/inscriptions/<int:inscription_id>', methods=['GET'])
def get_paiements_by_inscription(inscription_id):
    """Récupérer tous les paiements effectués par un élève (inscription)"""
    try:
        paiements = PaiementService.get_by_inscription(inscription_id)
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in paiements],
            'count': len(paiements)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@paiements_bp.route('/tranches/<int:tranche_paiement_id>/paiements', methods=['GET'])
def get_paiements_by_tranche(tranche_paiement_id):
    """Récupérer tous les paiements effectués pour une tranche donnée"""
    try:
        paiements = PaiementService.get_by_tranche(tranche_paiement_id)
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in paiements],
            'count': len(paiements)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@paiements_bp.route(
    '/inscriptions/<int:inscription_id>/situation/<int:annee_scolaire_id>/<int:classe_id>',
    methods=['GET']
)
def get_situation_financiere(inscription_id, annee_scolaire_id, classe_id):
    """Récupérer la situation financière (récapitulatif) d'un élève pour une année
    scolaire et une classe données (les tranches étant propres à une classe)."""
    try:
        situation = PaiementService.get_situation_financiere(inscription_id, annee_scolaire_id, classe_id)
        return jsonify({'success': True, 'data': situation}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@paiements_bp.route('', methods=['POST'])
def create_paiement():
    """Enregistrer un nouveau paiement.

    Un paiement couvre au minimum une tranche et au maximum n tranches, via
    le champ 'tranches' :
    {
        'inscription_id': int,
        'montant_verse': nombre,
        'date_paiement': date (optionnel),
        'mode_paiement': str (optionnel),
        'tranches': [
            {'tranche_paiement_id': int, 'montant_affecte': nombre},
            ...
        ]
    }
    La somme des montant_affecte doit être égale au montant_verse.
    """
    try:
        data = request.get_json()

        required_fields = ['inscription_id', 'montant_verse', 'tranches']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400

        if not isinstance(data.get('tranches'), list) or len(data['tranches']) < 1:
            return jsonify({
                'success': False,
                'error': "Le champ 'tranches' doit être une liste non vide d'au moins une tranche"
            }), 400

        paiement = PaiementService.create(data)
        return jsonify({'success': True, 'data': paiement.to_dict(), 'message': 'Paiement enregistré'}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@paiements_bp.route('/<int:id>', methods=['PUT'])
def update_paiement(id):
    """Mettre à jour un paiement.

    Si 'tranches' est fourni, il remplace entièrement la répartition existante
    et doit rester une liste d'au moins une tranche."""
    try:
        data = request.get_json()

        if 'tranches' in data and (not isinstance(data['tranches'], list) or len(data['tranches']) < 1):
            return jsonify({
                'success': False,
                'error': "Le champ 'tranches' doit être une liste non vide d'au moins une tranche"
            }), 400

        paiement = PaiementService.update(id, data)
        if paiement:
            return jsonify({'success': True, 'data': paiement.to_dict(), 'message': 'Paiement mis à jour'}), 200
        return jsonify({'success': False, 'error': 'Paiement non trouvé'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@paiements_bp.route('/<int:id>', methods=['DELETE'])
def delete_paiement(id):
    """Supprimer un paiement"""
    try:
        if PaiementService.delete(id):
            return jsonify({'success': True, 'message': 'Paiement supprimé'}), 200
        return jsonify({'success': False, 'error': 'Paiement non trouvé'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500