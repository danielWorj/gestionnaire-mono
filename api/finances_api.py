from flask import Blueprint, request, jsonify
from datetime import datetime
from decimal import Decimal

from services.finances_service import FinancesService

finances_bp = Blueprint('finances', __name__, url_prefix='/api/finances')


# ==================== CATÉGORIES D'ENTRÉES ====================

@finances_bp.route('/categories-entrees', methods=['GET'])
def get_all_categories_entrees():
    """Récupérer toutes les catégories d'entrées"""
    try:
        categories = FinancesService.get_all_categories_entree()
        return jsonify({
            'success': True,
            'data': [c.to_dict() for c in categories],
            'count': len(categories)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/categories-entrees/<int:id>', methods=['GET'])
def get_categorie_entree_by_id(id):
    """Récupérer une catégorie d'entrée par ID"""
    try:
        categorie = FinancesService.get_categorie_entree(id)
        if categorie:
            return jsonify({'success': True, 'data': categorie.to_dict(with_entrees=True)}), 200
        return jsonify({'success': False, 'error': 'Catégorie d\'entrée non trouvée'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/categories-entrees', methods=['POST'])
def create_categorie_entree():
    """Créer une nouvelle catégorie d'entrée"""
    try:
        data = request.get_json()

        if 'libelle' not in data:
            return jsonify({'success': False, 'error': 'Champ libelle requis'}), 400

        categorie = FinancesService.create_categorie_entree(
            libelle=data.get('libelle'),
            description=data.get('description')
        )
        return jsonify({
            'success': True,
            'data': categorie.to_dict(),
            'message': 'Catégorie d\'entrée créée'
        }), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/categories-entrees/<int:id>', methods=['PUT'])
def update_categorie_entree(id):
    """Mettre à jour une catégorie d'entrée"""
    try:
        data = request.get_json()
        categorie = FinancesService.update_categorie_entree(
            categorie_id=id,
            libelle=data.get('libelle'),
            description=data.get('description')
        )
        return jsonify({
            'success': True,
            'data': categorie.to_dict(),
            'message': 'Catégorie d\'entrée mise à jour'
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/categories-entrees/<int:id>', methods=['DELETE'])
def delete_categorie_entree(id):
    """Supprimer une catégorie d'entrée"""
    try:
        if FinancesService.delete_categorie_entree(id):
            return jsonify({'success': True, 'message': 'Catégorie d\'entrée supprimée'}), 200
        return jsonify({'success': False, 'error': 'Catégorie d\'entrée non trouvée'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== ENTRÉES (RECETTES) ====================

@finances_bp.route('/entrees', methods=['GET'])
def get_all_entrees():
    """Récupérer toutes les entrées"""
    try:
        entrees = FinancesService.get_all_entrees()
        return jsonify({
            'success': True,
            'data': [e.to_dict() for e in entrees],
            'count': len(entrees)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/entrees/<int:id>', methods=['GET'])
def get_entree_by_id(id):
    """Récupérer une entrée par ID avec ses sorties associées"""
    try:
        entree = FinancesService.get_entree(id)
        if entree:
            return jsonify({
                'success': True,
                'data': entree.to_dict(with_categorie=True, with_sorties=True)
            }), 200
        return jsonify({'success': False, 'error': 'Entrée non trouvée'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/categories-entrees/<int:categorie_id>/entrees', methods=['GET'])
def get_entrees_by_categorie(categorie_id):
    """Récupérer toutes les entrées d'une catégorie"""
    try:
        entrees = FinancesService.get_entrees_by_categorie(categorie_id)
        return jsonify({
            'success': True,
            'data': [e.to_dict() for e in entrees],
            'count': len(entrees)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/entrees/plage-dates', methods=['GET'])
def get_entrees_by_date_range():
    """Récupérer les entrées dans une plage de dates.
    
    Paramètres query requis:
        - date_debut: format YYYY-MM-DD
        - date_fin: format YYYY-MM-DD
    """
    try:
        date_debut_str = request.args.get('date_debut')
        date_fin_str = request.args.get('date_fin')

        if not date_debut_str or not date_fin_str:
            return jsonify({
                'success': False,
                'error': 'Paramètres date_debut et date_fin requis'
            }), 400

        date_debut = datetime.fromisoformat(date_debut_str).date()
        date_fin = datetime.fromisoformat(date_fin_str).date()

        entrees = FinancesService.get_entrees_by_date_range(date_debut, date_fin)
        return jsonify({
            'success': True,
            'data': [e.to_dict() for e in entrees],
            'count': len(entrees)
        }), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Format de date invalide. Utilisez YYYY-MM-DD'
        }), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/entrees', methods=['POST'])
def create_entree():
    """Créer une nouvelle entrée (recette)"""
    try:
        data = request.get_json()

        required_fields = ['libelle', 'categorie_entree_id', 'montant']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400

        date_entree = None
        if 'date' in data:
            date_entree = datetime.fromisoformat(data['date']).date()

        entree = FinancesService.create_entree(
            libelle=data.get('libelle'),
            categorie_entree_id=data.get('categorie_entree_id'),
            montant=Decimal(str(data.get('montant'))),
            date_entree=date_entree,
            description=data.get('description')
        )
        return jsonify({
            'success': True,
            'data': entree.to_dict(),
            'message': 'Entrée créée'
        }), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/entrees/<int:id>', methods=['PUT'])
def update_entree(id):
    """Mettre à jour une entrée"""
    try:
        data = request.get_json()

        date_entree = None
        if 'date' in data:
            date_entree = datetime.fromisoformat(data['date']).date()

        montant = None
        if 'montant' in data:
            montant = Decimal(str(data.get('montant')))

        entree = FinancesService.update_entree(
            entree_id=id,
            libelle=data.get('libelle'),
            montant=montant,
            date_entree=date_entree,
            description=data.get('description')
        )
        return jsonify({
            'success': True,
            'data': entree.to_dict(),
            'message': 'Entrée mise à jour'
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/entrees/<int:id>', methods=['DELETE'])
def delete_entree(id):
    """Supprimer une entrée"""
    try:
        if FinancesService.delete_entree(id):
            return jsonify({'success': True, 'message': 'Entrée supprimée'}), 200
        return jsonify({'success': False, 'error': 'Entrée non trouvée'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== CATÉGORIES DE SORTIES ====================

@finances_bp.route('/categories-sorties', methods=['GET'])
def get_all_categories_sorties():
    """Récupérer toutes les catégories de sorties"""
    try:
        categories = FinancesService.get_all_categories_sortie()
        return jsonify({
            'success': True,
            'data': [c.to_dict() for c in categories],
            'count': len(categories)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/categories-sorties/<int:id>', methods=['GET'])
def get_categorie_sortie_by_id(id):
    """Récupérer une catégorie de sortie par ID"""
    try:
        categorie = FinancesService.get_categorie_sortie(id)
        if categorie:
            return jsonify({'success': True, 'data': categorie.to_dict(with_sorties=True)}), 200
        return jsonify({'success': False, 'error': 'Catégorie de sortie non trouvée'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/categories-sorties', methods=['POST'])
def create_categorie_sortie():
    """Créer une nouvelle catégorie de sortie"""
    try:
        data = request.get_json()

        if 'libelle' not in data:
            return jsonify({'success': False, 'error': 'Champ libelle requis'}), 400

        categorie = FinancesService.create_categorie_sortie(
            libelle=data.get('libelle'),
            description=data.get('description')
        )
        return jsonify({
            'success': True,
            'data': categorie.to_dict(),
            'message': 'Catégorie de sortie créée'
        }), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/categories-sorties/<int:id>', methods=['PUT'])
def update_categorie_sortie(id):
    """Mettre à jour une catégorie de sortie"""
    try:
        data = request.get_json()
        categorie = FinancesService.update_categorie_sortie(
            categorie_id=id,
            libelle=data.get('libelle'),
            description=data.get('description')
        )
        return jsonify({
            'success': True,
            'data': categorie.to_dict(),
            'message': 'Catégorie de sortie mise à jour'
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/categories-sorties/<int:id>', methods=['DELETE'])
def delete_categorie_sortie(id):
    """Supprimer une catégorie de sortie"""
    try:
        if FinancesService.delete_categorie_sortie(id):
            return jsonify({'success': True, 'message': 'Catégorie de sortie supprimée'}), 200
        return jsonify({'success': False, 'error': 'Catégorie de sortie non trouvée'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== SORTIES (DÉPENSES) ====================

@finances_bp.route('/sorties', methods=['GET'])
def get_all_sorties():
    """Récupérer toutes les sorties"""
    try:
        sorties = FinancesService.get_all_sorties()
        return jsonify({
            'success': True,
            'data': [s.to_dict() for s in sorties],
            'count': len(sorties)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/sorties/<int:id>', methods=['GET'])
def get_sortie_by_id(id):
    """Récupérer une sortie par ID"""
    try:
        sortie = FinancesService.get_sortie(id)
        if sortie:
            return jsonify({
                'success': True,
                'data': sortie.to_dict(with_categorie=True, with_entree=True)
            }), 200
        return jsonify({'success': False, 'error': 'Sortie non trouvée'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/categories-sorties/<int:categorie_id>/sorties', methods=['GET'])
def get_sorties_by_categorie(categorie_id):
    """Récupérer toutes les sorties d'une catégorie"""
    try:
        sorties = FinancesService.get_sorties_by_categorie(categorie_id)
        return jsonify({
            'success': True,
            'data': [s.to_dict() for s in sorties],
            'count': len(sorties)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/sorties/plage-dates', methods=['GET'])
def get_sorties_by_date_range():
    """Récupérer les sorties dans une plage de dates.
    
    Paramètres query requis:
        - date_debut: format YYYY-MM-DD
        - date_fin: format YYYY-MM-DD
    """
    try:
        date_debut_str = request.args.get('date_debut')
        date_fin_str = request.args.get('date_fin')

        if not date_debut_str or not date_fin_str:
            return jsonify({
                'success': False,
                'error': 'Paramètres date_debut et date_fin requis'
            }), 400

        date_debut = datetime.fromisoformat(date_debut_str).date()
        date_fin = datetime.fromisoformat(date_fin_str).date()

        sorties = FinancesService.get_sorties_by_date_range(date_debut, date_fin)
        return jsonify({
            'success': True,
            'data': [s.to_dict() for s in sorties],
            'count': len(sorties)
        }), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Format de date invalide. Utilisez YYYY-MM-DD'
        }), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/entrees/<int:entree_id>/sorties', methods=['GET'])
def get_sorties_by_entree(entree_id):
    """Récupérer toutes les sorties rattachées à une entrée"""
    try:
        sorties = FinancesService.get_sorties_by_entree(entree_id)
        return jsonify({
            'success': True,
            'data': [s.to_dict() for s in sorties],
            'count': len(sorties)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/sorties', methods=['POST'])
def create_sortie():
    """Créer une nouvelle sortie (dépense)"""
    try:
        data = request.get_json()

        required_fields = ['libelle', 'categorie_sortie_id', 'montant']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400

        date_sortie = None
        if 'date' in data:
            date_sortie = datetime.fromisoformat(data['date']).date()

        sortie = FinancesService.create_sortie(
            libelle=data.get('libelle'),
            categorie_sortie_id=data.get('categorie_sortie_id'),
            montant=Decimal(str(data.get('montant'))),
            date_sortie=date_sortie,
            description=data.get('description'),
            entree_id=data.get('entree_id')
        )
        return jsonify({
            'success': True,
            'data': sortie.to_dict(),
            'message': 'Sortie créée'
        }), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/sorties/<int:id>', methods=['PUT'])
def update_sortie(id):
    """Mettre à jour une sortie"""
    try:
        data = request.get_json()

        date_sortie = None
        if 'date' in data:
            date_sortie = datetime.fromisoformat(data['date']).date()

        montant = None
        if 'montant' in data:
            montant = Decimal(str(data.get('montant')))

        sortie = FinancesService.update_sortie(
            sortie_id=id,
            libelle=data.get('libelle'),
            montant=montant,
            date_sortie=date_sortie,
            description=data.get('description')
        )
        return jsonify({
            'success': True,
            'data': sortie.to_dict(),
            'message': 'Sortie mise à jour'
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/sorties/<int:id>', methods=['DELETE'])
def delete_sortie(id):
    """Supprimer une sortie"""
    try:
        if FinancesService.delete_sortie(id):
            return jsonify({'success': True, 'message': 'Sortie supprimée'}), 200
        return jsonify({'success': False, 'error': 'Sortie non trouvée'}), 404
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== OPÉRATIONS DE LIAISON ====================

@finances_bp.route('/sorties/<int:sortie_id>/attacher-entree', methods=['POST'])
def attacher_sortie_a_entree(sortie_id):
    """Attacher une sortie à une entrée pour la financer"""
    try:
        data = request.get_json()

        if 'entree_id' not in data:
            return jsonify({'success': False, 'error': 'Champ entree_id requis'}), 400

        sortie = FinancesService.attacher_sortie_a_entree(
            sortie_id=sortie_id,
            entree_id=data.get('entree_id')
        )
        return jsonify({
            'success': True,
            'data': sortie.to_dict(),
            'message': 'Sortie attachée à l\'entrée'
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/sorties/<int:sortie_id>/detacher-entree', methods=['POST'])
def detacher_sortie_de_entree(sortie_id):
    """Détacher une sortie de son entrée de financement"""
    try:
        sortie = FinancesService.detacher_sortie_de_entree(sortie_id)
        return jsonify({
            'success': True,
            'data': sortie.to_dict(),
            'message': 'Sortie détachée de l\'entrée'
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== STATISTIQUES ET RAPPORTS ====================

@finances_bp.route('/totaux', methods=['GET'])
def get_totaux():
    """Récupérer les totaux (entrées, sorties, solde) avec filtrage par date optionnel.
    
    Paramètres query optionnels:
        - date_debut: format YYYY-MM-DD
        - date_fin: format YYYY-MM-DD
    """
    try:
        date_debut = None
        date_fin = None

        date_debut_str = request.args.get('date_debut')
        date_fin_str = request.args.get('date_fin')

        if date_debut_str:
            date_debut = datetime.fromisoformat(date_debut_str).date()
        if date_fin_str:
            date_fin = datetime.fromisoformat(date_fin_str).date()

        total_entrees = FinancesService.get_total_entrees(date_debut, date_fin)
        total_sorties = FinancesService.get_total_sorties(date_debut, date_fin)
        solde = FinancesService.get_solde(date_debut, date_fin)

        return jsonify({
            'success': True,
            'data': {
                'total_entrees': float(total_entrees),
                'total_sorties': float(total_sorties),
                'solde': float(solde),
                'date_debut': date_debut.isoformat() if date_debut else None,
                'date_fin': date_fin.isoformat() if date_fin else None
            }
        }), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Format de date invalide. Utilisez YYYY-MM-DD'
        }), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/stats/categories-entrees', methods=['GET'])
def get_stats_by_categorie_entree():
    """Récupérer les statistiques par catégorie d'entrée"""
    try:
        stats = FinancesService.get_stats_by_categorie_entree()
        return jsonify({
            'success': True,
            'data': stats,
            'count': len(stats)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/stats/categories-sorties', methods=['GET'])
def get_stats_by_categorie_sortie():
    """Récupérer les statistiques par catégorie de sortie"""
    try:
        stats = FinancesService.get_stats_by_categorie_sortie()
        return jsonify({
            'success': True,
            'data': stats,
            'count': len(stats)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/resume', methods=['GET'])
def get_resume_financier():
    """Récupérer un résumé complet de la situation financière.
    
    Paramètres query optionnels:
        - date_debut: format YYYY-MM-DD
        - date_fin: format YYYY-MM-DD
    """
    try:
        date_debut = None
        date_fin = None

        date_debut_str = request.args.get('date_debut')
        date_fin_str = request.args.get('date_fin')

        if date_debut_str:
            date_debut = datetime.fromisoformat(date_debut_str).date()
        if date_fin_str:
            date_fin = datetime.fromisoformat(date_fin_str).date()

        resume = FinancesService.get_resume_financier(date_debut, date_fin)
        return jsonify({'success': True, 'data': resume}), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Format de date invalide. Utilisez YYYY-MM-DD'
        }), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/entrees-non-financees', methods=['GET'])
def get_entrees_non_financees():
    """Récupérer les entrées qui n'ont pas toutes leurs sorties payées"""
    try:
        entrees = FinancesService.get_entrees_non_financees()
        return jsonify({
            'success': True,
            'data': [e.to_dict() for e in entrees],
            'count': len(entrees)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/sorties-non-financees', methods=['GET'])
def get_sorties_non_financees():
    """Récupérer les sorties qui ne sont pas attachées à une entrée"""
    try:
        sorties = FinancesService.get_sorties_non_financees()
        return jsonify({
            'success': True,
            'data': [s.to_dict() for s in sorties],
            'count': len(sorties)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@finances_bp.route('/entrees/<int:entree_id>/rapport', methods=['GET'])
def get_rapport_detaille_entree(entree_id):
    """Récupérer un rapport détaillé pour une entrée.
    
    Inclut les informations sur l'utilisation du montant (montant sorti,
    montant disponible, pourcentage d'utilisation) et les sorties associées.
    """
    try:
        rapport = FinancesService.get_rapport_detaille_entree(entree_id)
        return jsonify({'success': True, 'data': rapport}), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500