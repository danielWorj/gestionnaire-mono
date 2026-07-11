from models.paiements import TranchePaiement, Paiement
from models import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from decimal import Decimal, InvalidOperation
from datetime import datetime


# ==================== TRANCHE DE PAIEMENT ====================

class TranchePaiementService:
    """Service pour la gestion des tranches de paiement."""

    @staticmethod
    def get_all():
        return TranchePaiement.query.order_by(TranchePaiement.date_limite).all()

    @staticmethod
    def get_by_id(id):
        return TranchePaiement.query.get(id)

    @staticmethod
    def get_by_annee(annee_scolaire_id):
        """Récupère les tranches de paiement d'une année scolaire."""
        return TranchePaiement.query.filter_by(
            annee_scolaire_id=annee_scolaire_id
        ).order_by(TranchePaiement.date_limite).all()

    @staticmethod
    def create(data):
        try:
            try:
                montant_attendu = Decimal(str(data.get('montant_attendu', 0)))
            except (InvalidOperation, TypeError):
                raise ValueError("Le montant attendu doit être un nombre valide")

            if montant_attendu <= 0:
                raise ValueError("Le montant attendu doit être positif")

            tranche = TranchePaiement(
                annee_scolaire_id=data['annee_scolaire_id'],
                libelle=data['libelle'],
                montant_attendu=montant_attendu,
                date_limite=data.get('date_limite')
            )
            db.session.add(tranche)
            db.session.commit()
            return tranche
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Erreur lors de la création de la tranche de paiement")

    @staticmethod
    def update(id, data):
        tranche = TranchePaiement.query.get(id)
        if not tranche:
            return None

        try:
            if 'libelle' in data:
                tranche.libelle = data['libelle']

            if 'montant_attendu' in data:
                try:
                    montant_attendu = Decimal(str(data['montant_attendu']))
                except (InvalidOperation, TypeError):
                    raise ValueError("Le montant attendu doit être un nombre valide")
                if montant_attendu <= 0:
                    raise ValueError("Le montant attendu doit être positif")
                tranche.montant_attendu = montant_attendu

            if 'date_limite' in data:
                tranche.date_limite = data['date_limite']

            if 'annee_scolaire_id' in data:
                tranche.annee_scolaire_id = data['annee_scolaire_id']

            db.session.commit()
            return tranche
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Erreur lors de la mise à jour de la tranche de paiement")

    @staticmethod
    def delete(id):
        tranche = TranchePaiement.query.get(id)
        if not tranche:
            return False

        try:
            db.session.delete(tranche)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Impossible de supprimer cette tranche (paiements liés existants)")

    @staticmethod
    def get_total_verse(tranche_paiement_id):
        """Total versé (toutes inscriptions confondues) pour une tranche donnée."""
        total = db.session.query(func.sum(Paiement.montant_verse)).filter(
            Paiement.tranche_paiement_id == tranche_paiement_id
        ).scalar()
        return float(total) if total else 0.0


# ==================== PAIEMENT ====================

class PaiementService:
    """Service pour la gestion des paiements."""

    @staticmethod
    def get_all():
        return Paiement.query.order_by(Paiement.date_paiement.desc()).all()

    @staticmethod
    def get_by_id(id):
        return Paiement.query.get(id)

    @staticmethod
    def get_by_inscription(inscription_id):
        """Récupère tous les paiements effectués pour un élève (inscription) donné."""
        return Paiement.query.filter_by(
            inscription_id=inscription_id
        ).order_by(Paiement.date_paiement.desc()).all()

    @staticmethod
    def get_by_tranche(tranche_paiement_id):
        """Récupère tous les paiements effectués pour une tranche donnée."""
        return Paiement.query.filter_by(tranche_paiement_id=tranche_paiement_id).all()

    @staticmethod
    def get_by_inscription_tranche(inscription_id, tranche_paiement_id):
        """Récupère les paiements d'un élève pour une tranche précise."""
        return Paiement.query.filter_by(
            inscription_id=inscription_id,
            tranche_paiement_id=tranche_paiement_id
        ).all()

    @staticmethod
    def create(data):
        try:
            try:
                montant_verse = Decimal(str(data.get('montant_verse', 0)))
            except (InvalidOperation, TypeError):
                raise ValueError("Le montant versé doit être un nombre valide")

            if montant_verse <= 0:
                raise ValueError("Le montant versé doit être positif")

            tranche = TranchePaiement.query.get(data['tranche_paiement_id'])
            if not tranche:
                raise ValueError("Tranche de paiement non trouvée")

            paiement = Paiement(
                inscription_id=data['inscription_id'],
                tranche_paiement_id=data['tranche_paiement_id'],
                montant_verse=montant_verse,
                date_paiement=data.get('date_paiement', datetime.utcnow().date()),
                mode_paiement=data.get('mode_paiement')
            )
            db.session.add(paiement)
            db.session.commit()
            return paiement
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Erreur lors de l'enregistrement du paiement")

    @staticmethod
    def update(id, data):
        paiement = Paiement.query.get(id)
        if not paiement:
            return None

        try:
            if 'montant_verse' in data:
                try:
                    montant_verse = Decimal(str(data['montant_verse']))
                except (InvalidOperation, TypeError):
                    raise ValueError("Le montant versé doit être un nombre valide")
                if montant_verse <= 0:
                    raise ValueError("Le montant versé doit être positif")
                paiement.montant_verse = montant_verse

            if 'date_paiement' in data:
                paiement.date_paiement = data['date_paiement']

            if 'mode_paiement' in data:
                paiement.mode_paiement = data['mode_paiement']

            if 'tranche_paiement_id' in data:
                tranche = TranchePaiement.query.get(data['tranche_paiement_id'])
                if not tranche:
                    raise ValueError("Tranche de paiement non trouvée")
                paiement.tranche_paiement_id = data['tranche_paiement_id']

            db.session.commit()
            return paiement
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Erreur lors de la mise à jour du paiement")

    @staticmethod
    def delete(id):
        paiement = Paiement.query.get(id)
        if not paiement:
            return False

        try:
            db.session.delete(paiement)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Impossible de supprimer ce paiement")

    @staticmethod
    def get_situation_financiere(inscription_id, annee_scolaire_id):
        """
        Récapitulatif de la situation financière d'un élève (inscription) pour une année scolaire.

        Pour chaque tranche de l'année: montant attendu, total versé, solde restant et statut
        ('Impayé', 'Partiel', 'Soldé'), ainsi que les totaux généraux sur l'année.

        Args:
            inscription_id: ID de l'inscription de l'élève
            annee_scolaire_id: ID de l'année scolaire

        Returns:
            dict: détail par tranche + totaux (montant attendu, versé, solde global)
        """
        tranches = TranchePaiement.query.filter_by(
            annee_scolaire_id=annee_scolaire_id
        ).order_by(TranchePaiement.date_limite).all()

        detail = []
        total_attendu = Decimal('0')
        total_verse = Decimal('0')

        for tranche in tranches:
            paiements = Paiement.query.filter_by(
                inscription_id=inscription_id,
                tranche_paiement_id=tranche.id
            ).all()

            verse_tranche = sum((p.montant_verse for p in paiements), Decimal('0'))
            solde = tranche.montant_attendu - verse_tranche

            if verse_tranche <= 0:
                statut = 'Impayé'
            elif solde <= 0:
                statut = 'Soldé'
            else:
                statut = 'Partiel'

            detail.append({
                'tranche_id': tranche.id,
                'libelle': tranche.libelle,
                'date_limite': tranche.date_limite.isoformat() if tranche.date_limite else None,
                'montant_attendu': float(tranche.montant_attendu),
                'montant_verse': float(verse_tranche),
                'solde': float(solde),
                'statut': statut
            })

            total_attendu += tranche.montant_attendu
            total_verse += verse_tranche

        return {
            'inscription_id': inscription_id,
            'annee_scolaire_id': annee_scolaire_id,
            'tranches': detail,
            'total_attendu': float(total_attendu),
            'total_verse': float(total_verse),
            'solde_global': float(total_attendu - total_verse)
        }