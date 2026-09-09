"""Service de gestion des finances.

Fournit les opérations métier pour gérer les catégories et les mouvements
financiers (entrées et sorties).
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models import db
from models.finances import (
    CategorieEntree,
    Entree,
    CategorieSortie,
    Sortie
)


class FinancesService:
    """Service centralisé pour la gestion des finances."""

    # ============================================================================
    # GESTION DES CATÉGORIES D'ENTRÉES
    # ============================================================================

    @staticmethod
    def create_categorie_entree(libelle: str, description: str = None) -> CategorieEntree:
        """Crée une nouvelle catégorie d'entrée.

        Args:
            libelle: Nom unique de la catégorie
            description: Description optionnelle

        Returns:
            CategorieEntree: La catégorie créée

        Raises:
            ValueError: Si le libellé est vide ou existe déjà
            SQLAlchemyError: En cas d'erreur base de données
        """
        if not libelle or not libelle.strip():
            raise ValueError("Le libellé de la catégorie d'entrée est obligatoire")

        try:
            categorie = CategorieEntree(
                libelle=libelle.strip(),
                description=description
            )
            db.session.add(categorie)
            db.session.commit()
            return categorie
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"Une catégorie d'entrée avec le libellé '{libelle}' existe déjà")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise

    @staticmethod
    def get_categorie_entree(categorie_id: int) -> Optional[CategorieEntree]:
        """Récupère une catégorie d'entrée par ID."""
        return CategorieEntree.query.get(categorie_id)

    @staticmethod
    def get_all_categories_entree() -> List[CategorieEntree]:
        """Récupère toutes les catégories d'entrée."""
        return CategorieEntree.query.all()

    @staticmethod
    def update_categorie_entree(
        categorie_id: int,
        libelle: str = None,
        description: str = None
    ) -> CategorieEntree:
        """Met à jour une catégorie d'entrée.

        Args:
            categorie_id: ID de la catégorie
            libelle: Nouveau libellé (optionnel)
            description: Nouvelle description (optionnelle)

        Returns:
            CategorieEntree: La catégorie mise à jour

        Raises:
            ValueError: Si la catégorie n'existe pas ou le libellé est invalide
        """
        categorie = FinancesService.get_categorie_entree(categorie_id)
        if not categorie:
            raise ValueError(f"Catégorie d'entrée {categorie_id} non trouvée")

        try:
            if libelle is not None:
                categorie.libelle = libelle.strip()
            if description is not None:
                categorie.description = description

            db.session.commit()
            return categorie
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"Le libellé '{libelle}' est déjà utilisé")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise

    @staticmethod
    def delete_categorie_entree(categorie_id: int) -> bool:
        """Supprime une catégorie d'entrée.

        Args:
            categorie_id: ID de la catégorie

        Returns:
            bool: True si supprimée, False si non trouvée

        Raises:
            ValueError: Si la catégorie a des entrées associées
        """
        categorie = FinancesService.get_categorie_entree(categorie_id)
        if not categorie:
            return False

        if categorie.entrees:
            raise ValueError(
                f"Impossible de supprimer la catégorie : elle contient {len(categorie.entrees)} entrée(s)"
            )

        try:
            db.session.delete(categorie)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise

    # ============================================================================
    # GESTION DES ENTRÉES (RECETTES)
    # ============================================================================

    @staticmethod
    def create_entree(
        libelle: str,
        categorie_entree_id: int,
        montant: Decimal,
        date_entree: date = None,
        description: str = None
    ) -> Entree:
        """Crée une nouvelle entrée financière.

        Args:
            libelle: Nom de l'entrée
            categorie_entree_id: ID de la catégorie
            montant: Montant de l'entrée (doit être > 0)
            date_entree: Date de l'entrée (défaut: aujourd'hui)
            description: Description optionnelle

        Returns:
            Entree: L'entrée créée

        Raises:
            ValueError: Si les paramètres sont invalides
        """
        if not libelle or not libelle.strip():
            raise ValueError("Le libellé de l'entrée est obligatoire")

        categorie = FinancesService.get_categorie_entree(categorie_entree_id)
        if not categorie:
            raise ValueError(f"Catégorie d'entrée {categorie_entree_id} non trouvée")

        montant_decimal = Decimal(str(montant))
        if montant_decimal <= 0:
            raise ValueError("Le montant de l'entrée doit être positif")

        try:
            entree = Entree(
                libelle=libelle.strip(),
                description=description,
                categorie_entree_id=categorie_entree_id,
                montant=montant_decimal,
                date=date_entree or datetime.utcnow().date()
            )
            db.session.add(entree)
            db.session.commit()
            return entree
        except SQLAlchemyError as e:
            db.session.rollback()
            raise

    @staticmethod
    def get_entree(entree_id: int) -> Optional[Entree]:
        """Récupère une entrée par ID."""
        return Entree.query.get(entree_id)

    @staticmethod
    def get_all_entrees() -> List[Entree]:
        """Récupère toutes les entrées."""
        return Entree.query.all()

    @staticmethod
    def get_entrees_by_categorie(categorie_id: int) -> List[Entree]:
        """Récupère toutes les entrées d'une catégorie."""
        return Entree.query.filter_by(categorie_entree_id=categorie_id).all()

    @staticmethod
    def get_entrees_by_date_range(
        date_debut: date,
        date_fin: date
    ) -> List[Entree]:
        """Récupère les entrées dans une plage de dates."""
        return Entree.query.filter(
            Entree.date.between(date_debut, date_fin)
        ).all()

    @staticmethod
    def update_entree(
        entree_id: int,
        libelle: str = None,
        montant: Decimal = None,
        date_entree: date = None,
        description: str = None
    ) -> Entree:
        """Met à jour une entrée.

        Args:
            entree_id: ID de l'entrée
            libelle: Nouveau libellé (optionnel)
            montant: Nouveau montant (optionnel, doit être > 0)
            date_entree: Nouvelle date (optionnelle)
            description: Nouvelle description (optionnelle)

        Returns:
            Entree: L'entrée mise à jour
        """
        entree = FinancesService.get_entree(entree_id)
        if not entree:
            raise ValueError(f"Entrée {entree_id} non trouvée")

        try:
            if libelle is not None:
                entree.libelle = libelle.strip()
            if montant is not None:
                montant_decimal = Decimal(str(montant))
                if montant_decimal <= 0:
                    raise ValueError("Le montant de l'entrée doit être positif")
                entree.montant = montant_decimal
            if date_entree is not None:
                entree.date = date_entree
            if description is not None:
                entree.description = description

            db.session.commit()
            return entree
        except SQLAlchemyError as e:
            db.session.rollback()
            raise

    @staticmethod
    def delete_entree(entree_id: int) -> bool:
        """Supprime une entrée.

        Args:
            entree_id: ID de l'entrée

        Returns:
            bool: True si supprimée, False si non trouvée

        Raises:
            ValueError: Si l'entrée finance des sorties
        """
        entree = FinancesService.get_entree(entree_id)
        if not entree:
            return False

        if entree.sorties:
            raise ValueError(
                f"Impossible de supprimer l'entrée : elle finance {len(entree.sorties)} sortie(s)"
            )

        try:
            db.session.delete(entree)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise

    # ============================================================================
    # GESTION DES CATÉGORIES DE SORTIES
    # ============================================================================

    @staticmethod
    def create_categorie_sortie(libelle: str, description: str = None) -> CategorieSortie:
        """Crée une nouvelle catégorie de sortie.

        Args:
            libelle: Nom unique de la catégorie
            description: Description optionnelle

        Returns:
            CategorieSortie: La catégorie créée

        Raises:
            ValueError: Si le libellé est vide ou existe déjà
        """
        if not libelle or not libelle.strip():
            raise ValueError("Le libellé de la catégorie de sortie est obligatoire")

        try:
            categorie = CategorieSortie(
                libelle=libelle.strip(),
                description=description
            )
            db.session.add(categorie)
            db.session.commit()
            return categorie
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"Une catégorie de sortie avec le libellé '{libelle}' existe déjà")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise

    @staticmethod
    def get_categorie_sortie(categorie_id: int) -> Optional[CategorieSortie]:
        """Récupère une catégorie de sortie par ID."""
        return CategorieSortie.query.get(categorie_id)

    @staticmethod
    def get_all_categories_sortie() -> List[CategorieSortie]:
        """Récupère toutes les catégories de sortie."""
        return CategorieSortie.query.all()

    @staticmethod
    def update_categorie_sortie(
        categorie_id: int,
        libelle: str = None,
        description: str = None
    ) -> CategorieSortie:
        """Met à jour une catégorie de sortie."""
        categorie = FinancesService.get_categorie_sortie(categorie_id)
        if not categorie:
            raise ValueError(f"Catégorie de sortie {categorie_id} non trouvée")

        try:
            if libelle is not None:
                categorie.libelle = libelle.strip()
            if description is not None:
                categorie.description = description

            db.session.commit()
            return categorie
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"Le libellé '{libelle}' est déjà utilisé")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise

    @staticmethod
    def delete_categorie_sortie(categorie_id: int) -> bool:
        """Supprime une catégorie de sortie.

        Raises:
            ValueError: Si la catégorie a des sorties associées
        """
        categorie = FinancesService.get_categorie_sortie(categorie_id)
        if not categorie:
            return False

        if categorie.sorties:
            raise ValueError(
                f"Impossible de supprimer la catégorie : elle contient {len(categorie.sorties)} sortie(s)"
            )

        try:
            db.session.delete(categorie)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise

    # ============================================================================
    # GESTION DES SORTIES (DÉPENSES)
    # ============================================================================

    @staticmethod
    def create_sortie(
        libelle: str,
        categorie_sortie_id: int,
        montant: Decimal,
        date_sortie: date = None,
        entree_id: int = None,
        description: str = None
    ) -> Sortie:
        """Crée une nouvelle sortie financière.

        Args:
            libelle: Nom de la sortie
            categorie_sortie_id: ID de la catégorie
            montant: Montant de la sortie (doit être > 0)
            date_sortie: Date de la sortie (défaut: aujourd'hui)
            entree_id: ID de l'entrée qui finance cette sortie (optionnel)
            description: Description optionnelle

        Returns:
            Sortie: La sortie créée

        Raises:
            ValueError: Si les paramètres sont invalides
        """
        if not libelle or not libelle.strip():
            raise ValueError("Le libellé de la sortie est obligatoire")

        categorie = FinancesService.get_categorie_sortie(categorie_sortie_id)
        if not categorie:
            raise ValueError(f"Catégorie de sortie {categorie_sortie_id} non trouvée")

        montant_decimal = Decimal(str(montant))
        if montant_decimal <= 0:
            raise ValueError("Le montant de la sortie doit être positif")

        # Vérifier que l'entree existe si spécifiée
        if entree_id is not None:
            entree = FinancesService.get_entree(entree_id)
            if not entree:
                raise ValueError(f"Entrée {entree_id} non trouvée")

            # Vérifier que le montant disponible est suffisant
            if montant_decimal > Decimal(str(entree.montant_disponible)):
                raise ValueError(
                    f"Montant insuffisant : l'entrée n'a que {entree.montant_disponible} disponible"
                )

        try:
            sortie = Sortie(
                libelle=libelle.strip(),
                description=description,
                montant=montant_decimal,
                date=date_sortie or datetime.utcnow().date(),
                categorie_sortie_id=categorie_sortie_id,
                entree_id=entree_id
            )
            db.session.add(sortie)
            db.session.commit()
            return sortie
        except SQLAlchemyError as e:
            db.session.rollback()
            raise

    @staticmethod
    def get_sortie(sortie_id: int) -> Optional[Sortie]:
        """Récupère une sortie par ID."""
        return Sortie.query.get(sortie_id)

    @staticmethod
    def get_all_sorties() -> List[Sortie]:
        """Récupère toutes les sorties."""
        return Sortie.query.all()

    @staticmethod
    def get_sorties_by_categorie(categorie_id: int) -> List[Sortie]:
        """Récupère toutes les sorties d'une catégorie."""
        return Sortie.query.filter_by(categorie_sortie_id=categorie_id).all()

    @staticmethod
    def get_sorties_by_entree(entree_id: int) -> List[Sortie]:
        """Récupère toutes les sorties financées par une entrée."""
        return Sortie.query.filter_by(entree_id=entree_id).all()

    @staticmethod
    def get_sorties_by_date_range(
        date_debut: date,
        date_fin: date
    ) -> List[Sortie]:
        """Récupère les sorties dans une plage de dates."""
        return Sortie.query.filter(
            Sortie.date.between(date_debut, date_fin)
        ).all()

    @staticmethod
    def update_sortie(
        sortie_id: int,
        libelle: str = None,
        montant: Decimal = None,
        date_sortie: date = None,
        entree_id: int = None,
        description: str = None
    ) -> Sortie:
        """Met à jour une sortie."""
        sortie = FinancesService.get_sortie(sortie_id)
        if not sortie:
            raise ValueError(f"Sortie {sortie_id} non trouvée")

        try:
            if libelle is not None:
                sortie.libelle = libelle.strip()
            if montant is not None:
                montant_decimal = Decimal(str(montant))
                if montant_decimal <= 0:
                    raise ValueError("Le montant de la sortie doit être positif")
                sortie.montant = montant_decimal
            if date_sortie is not None:
                sortie.date = date_sortie
            if entree_id is not None:
                entree = FinancesService.get_entree(entree_id)
                if not entree:
                    raise ValueError(f"Entrée {entree_id} non trouvée")
                sortie.entree_id = entree_id
            if description is not None:
                sortie.description = description

            db.session.commit()
            return sortie
        except SQLAlchemyError as e:
            db.session.rollback()
            raise

    @staticmethod
    def delete_sortie(sortie_id: int) -> bool:
        """Supprime une sortie.

        Returns:
            bool: True si supprimée, False si non trouvée
        """
        sortie = FinancesService.get_sortie(sortie_id)
        if not sortie:
            return False

        try:
            db.session.delete(sortie)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise

    @staticmethod
    def attacher_sortie_a_entree(sortie_id: int, entree_id: int) -> Sortie:
        """Attache une sortie à une entrée pour la financer.

        Raises:
            ValueError: Si les montants ne sont pas cohérents
        """
        sortie = FinancesService.get_sortie(sortie_id)
        if not sortie:
            raise ValueError(f"Sortie {sortie_id} non trouvée")

        entree = FinancesService.get_entree(entree_id)
        if not entree:
            raise ValueError(f"Entrée {entree_id} non trouvée")

        # Vérifier que le montant disponible est suffisant
        if Decimal(str(sortie.montant)) > Decimal(str(entree.montant_disponible)):
            raise ValueError(
                f"Montant insuffisant : l'entrée n'a que {entree.montant_disponible} disponible"
            )

        try:
            sortie.entree_id = entree_id
            db.session.commit()
            return sortie
        except SQLAlchemyError as e:
            db.session.rollback()
            raise

    @staticmethod
    def detacher_sortie_de_entree(sortie_id: int) -> Sortie:
        """Détache une sortie de son entrée de financement."""
        sortie = FinancesService.get_sortie(sortie_id)
        if not sortie:
            raise ValueError(f"Sortie {sortie_id} non trouvée")

        try:
            sortie.entree_id = None
            db.session.commit()
            return sortie
        except SQLAlchemyError as e:
            db.session.rollback()
            raise

    # ============================================================================
    # OPÉRATIONS MÉTIER / STATISTIQUES
    # ============================================================================

    @staticmethod
    def get_total_entrees(
        date_debut: date = None,
        date_fin: date = None
    ) -> Decimal:
        """Calcule le total des entrées.

        Args:
            date_debut: Date de début (optionnelle)
            date_fin: Date de fin (optionnelle)

        Returns:
            Decimal: Total des entrées
        """
        query = Entree.query
        if date_debut:
            query = query.filter(Entree.date >= date_debut)
        if date_fin:
            query = query.filter(Entree.date <= date_fin)

        entrees = query.all()
        return sum(
            (Decimal(str(e.montant)) for e in entrees),
            Decimal('0')
        )

    @staticmethod
    def get_total_sorties(
        date_debut: date = None,
        date_fin: date = None
    ) -> Decimal:
        """Calcule le total des sorties.

        Args:
            date_debut: Date de début (optionnelle)
            date_fin: Date de fin (optionnelle)

        Returns:
            Decimal: Total des sorties
        """
        query = Sortie.query
        if date_debut:
            query = query.filter(Sortie.date >= date_debut)
        if date_fin:
            query = query.filter(Sortie.date <= date_fin)

        sorties = query.all()
        return sum(
            (Decimal(str(s.montant)) for s in sorties),
            Decimal('0')
        )

    @staticmethod
    def get_solde(
        date_debut: date = None,
        date_fin: date = None
    ) -> Decimal:
        """Calcule le solde (entrées - sorties).

        Args:
            date_debut: Date de début (optionnelle)
            date_fin: Date de fin (optionnelle)

        Returns:
            Decimal: Solde (positif si excédentaire, négatif si déficitaire)
        """
        total_entrees = FinancesService.get_total_entrees(date_debut, date_fin)
        total_sorties = FinancesService.get_total_sorties(date_debut, date_fin)
        return total_entrees - total_sorties

    @staticmethod
    def get_stats_by_categorie_entree() -> List[Dict]:
        """Obtient les statistiques par catégorie d'entrée.

        Returns:
            List[Dict]: Liste contenant {categorie, total, nombre_entrees}
        """
        categories = CategorieEntree.query.all()
        stats = []

        for cat in categories:
            total = sum(
                (Decimal(str(e.montant)) for e in cat.entrees),
                Decimal('0')
            )
            stats.append({
                'categorie': cat.to_dict(),
                'total': float(total),
                'nombre_entrees': len(cat.entrees)
            })

        return stats

    @staticmethod
    def get_stats_by_categorie_sortie() -> List[Dict]:
        """Obtient les statistiques par catégorie de sortie.

        Returns:
            List[Dict]: Liste contenant {categorie, total, nombre_sorties}
        """
        categories = CategorieSortie.query.all()
        stats = []

        for cat in categories:
            total = sum(
                (Decimal(str(s.montant)) for s in cat.sorties),
                Decimal('0')
            )
            stats.append({
                'categorie': cat.to_dict(),
                'total': float(total),
                'nombre_sorties': len(cat.sorties)
            })

        return stats

    @staticmethod
    def get_resume_financier(
        date_debut: date = None,
        date_fin: date = None
    ) -> Dict:
        """Obtient un résumé complet de la situation financière.

        Args:
            date_debut: Date de début (optionnelle)
            date_fin: Date de fin (optionnelle)

        Returns:
            Dict: Résumé contenant {total_entrees, total_sorties, solde, details}
        """
        total_entrees = FinancesService.get_total_entrees(date_debut, date_fin)
        total_sorties = FinancesService.get_total_sorties(date_debut, date_fin)
        solde = total_entrees - total_sorties

        return {
            'total_entrees': float(total_entrees),
            'total_sorties': float(total_sorties),
            'solde': float(solde),
            'date_debut': date_debut.isoformat() if date_debut else None,
            'date_fin': date_fin.isoformat() if date_fin else None,
            'stats_entrees': FinancesService.get_stats_by_categorie_entree(),
            'stats_sorties': FinancesService.get_stats_by_categorie_sortie(),
        }

    @staticmethod
    def get_entrees_non_financees() -> List[Entree]:
        """Retourne les entrées qui n'ont pas toutes leurs sorties associées."""
        entrees = Entree.query.all()
        return [e for e in entrees if e.montant_disponible > 0]

    @staticmethod
    def get_sorties_non_financees() -> List[Sortie]:
        """Retourne les sorties qui ne sont pas attachées à une entrée."""
        return Sortie.query.filter_by(entree_id=None).all()

    @staticmethod
    def get_rapport_detaille_entree(entree_id: int) -> Dict:
        """Obtient un rapport détaillé pour une entrée.

        Args:
            entree_id: ID de l'entrée

        Returns:
            Dict: Rapport contenant informations et sorties associées
        """
        entree = FinancesService.get_entree(entree_id)
        if not entree:
            raise ValueError(f"Entrée {entree_id} non trouvée")

        return {
            'entree': entree.to_dict(with_sorties=True),
            'montant_total': float(entree.montant),
            'montant_sorti': float(entree.montant_sorti),
            'montant_disponible': float(entree.montant_disponible),
            'pourcentage_utilise': float(
                (entree.montant_sorti / entree.montant * 100) if entree.montant > 0 else 0
            ),
            'nombre_sorties': len(entree.sorties)
        }