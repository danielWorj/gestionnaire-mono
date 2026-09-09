from models.paiements import TranchePaiement, Paiement, PaiementTranche
from models import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from decimal import Decimal, InvalidOperation
from datetime import datetime


# ==================== TRANCHE DE PAIEMENT ====================

class TranchePaiementService:
    """Service pour la gestion des tranches de paiement.

    Une tranche est désormais rattachée à la fois à une année scolaire ET à
    une classe (classe_id), les montants attendus pouvant différer d'une
    classe à l'autre pour une même année scolaire.
    """

    @staticmethod
    def get_all():
        return TranchePaiement.query.order_by(TranchePaiement.date_limite).all()

    @staticmethod
    def get_by_id(id):
        return TranchePaiement.query.get(id)

    @staticmethod
    def get_by_annee(annee_scolaire_id):
        """Récupère les tranches de paiement d'une année scolaire (toutes classes confondues)."""
        return TranchePaiement.query.filter_by(
            annee_scolaire_id=annee_scolaire_id
        ).order_by(TranchePaiement.date_limite).all()

    @staticmethod
    def get_by_classe(classe_id):
        """Récupère les tranches de paiement d'une classe (toutes années confondues)."""
        return TranchePaiement.query.filter_by(
            classe_id=classe_id
        ).order_by(TranchePaiement.date_limite).all()

    @staticmethod
    def get_by_annee_classe(annee_scolaire_id, classe_id):
        """Récupère les tranches de paiement d'une classe pour une année scolaire donnée."""
        return TranchePaiement.query.filter_by(
            annee_scolaire_id=annee_scolaire_id,
            classe_id=classe_id
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
                classe_id=data['classe_id'],
                libelle=data['libelle'],
                montant_attendu=montant_attendu,
                date_limite=data.get('date_limite')
            )
            db.session.add(tranche)
            db.session.commit()
            return tranche
        except IntegrityError:
            db.session.rollback()
            raise ValueError(
                "Erreur lors de la création de la tranche de paiement "
                "(une tranche avec ce libellé existe peut-être déjà pour cette classe et cette année)"
            )

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

            if 'classe_id' in data:
                tranche.classe_id = data['classe_id']

            db.session.commit()
            return tranche
        except IntegrityError:
            db.session.rollback()
            raise ValueError(
                "Erreur lors de la mise à jour de la tranche de paiement "
                "(conflit avec une tranche existante pour cette classe et cette année)"
            )

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
        """Total versé (toutes inscriptions confondues) pour une tranche donnée.

        Le total correspond désormais à la somme des montants affectés à cette
        tranche via la table d'association PaiementTranche (un même paiement
        pouvant répartir son montant sur plusieurs tranches).
        """
        total = db.session.query(func.sum(PaiementTranche.montant_affecte)).filter(
            PaiementTranche.tranche_paiement_id == tranche_paiement_id
        ).scalar()
        return float(total) if total else 0.0


# ==================== PAIEMENT ====================

class PaiementService:
    """Service pour la gestion des paiements.

    Un paiement couvre au minimum une tranche et au maximum n tranches. La
    répartition du montant versé entre les tranches est portée par la table
    d'association PaiementTranche (voir Paiement.tranches).
    """

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
        """Récupère tous les paiements ayant une allocation sur une tranche donnée."""
        return Paiement.query.join(PaiementTranche).filter(
            PaiementTranche.tranche_paiement_id == tranche_paiement_id
        ).order_by(Paiement.date_paiement.desc()).all()

    @staticmethod
    def get_by_inscription_tranche(inscription_id, tranche_paiement_id):
        """Récupère les paiements d'un élève ayant une allocation sur une tranche précise."""
        return Paiement.query.join(PaiementTranche).filter(
            Paiement.inscription_id == inscription_id,
            PaiementTranche.tranche_paiement_id == tranche_paiement_id
        ).all()

    # ---------- Helpers internes ----------

    @staticmethod
    def _construire_lignes_tranches(tranches_data):
        """Valide et construit les lignes de répartition (tranche, montant).

        tranches_data: liste de dicts {'tranche_paiement_id': int, 'montant_affecte': ...}

        Retourne (lignes, total) où lignes est une liste de tuples
        (tranche_paiement_id, Decimal montant_affecte) et total la somme Decimal.
        """
        if not tranches_data:
            raise ValueError("Un paiement doit couvrir au moins une tranche de paiement")

        lignes = []
        vus = set()
        total = Decimal('0')

        for item in tranches_data:
            tranche_id = item.get('tranche_paiement_id')
            if tranche_id is None:
                raise ValueError("tranche_paiement_id manquant dans une ligne de répartition")

            if tranche_id in vus:
                raise ValueError("Une même tranche ne peut être affectée qu'une seule fois par paiement")
            vus.add(tranche_id)

            tranche = TranchePaiement.query.get(tranche_id)
            if not tranche:
                raise ValueError(f"Tranche de paiement {tranche_id} non trouvée")

            try:
                montant_affecte = Decimal(str(item.get('montant_affecte', 0)))
            except (InvalidOperation, TypeError):
                raise ValueError("Le montant affecté à une tranche doit être un nombre valide")

            if montant_affecte <= 0:
                raise ValueError("Le montant affecté à une tranche doit être positif")

            lignes.append((tranche_id, montant_affecte))
            total += montant_affecte

        return lignes, total

    # ---------- CRUD ----------

    @staticmethod
    def create(data):
        """Crée un paiement et sa répartition sur une ou plusieurs tranches.

        data attendu:
        {
            'inscription_id': int,
            'montant_verse': nombre,
            'date_paiement': date (optionnel),
            'mode_paiement': str (optionnel),
            'tranches': [
                {'tranche_paiement_id': int, 'montant_affecte': nombre},
                ...
            ]  # au moins 1 ligne, au maximum n
        }

        La somme des montant_affecte doit être égale au montant_verse.
        """
        try:
            try:
                montant_verse = Decimal(str(data.get('montant_verse', 0)))
            except (InvalidOperation, TypeError):
                raise ValueError("Le montant versé doit être un nombre valide")

            if montant_verse <= 0:
                raise ValueError("Le montant versé doit être positif")

            lignes, total_affecte = PaiementService._construire_lignes_tranches(
                data.get('tranches') or []
            )

            if total_affecte != montant_verse:
                raise ValueError(
                    f"La somme des montants affectés aux tranches ({total_affecte}) "
                    f"doit être égale au montant versé ({montant_verse})"
                )

            paiement = Paiement(
                inscription_id=data['inscription_id'],
                montant_verse=montant_verse,
                date_paiement=data.get('date_paiement', datetime.utcnow().date()),
                mode_paiement=data.get('mode_paiement')
            )

            for tranche_paiement_id, montant_affecte in lignes:
                paiement.tranches.append(PaiementTranche(
                    tranche_paiement_id=tranche_paiement_id,
                    montant_affecte=montant_affecte
                ))

            db.session.add(paiement)
            db.session.commit()
            return paiement
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Erreur lors de l'enregistrement du paiement")

    @staticmethod
    def update(id, data):
        """Met à jour un paiement.

        Si 'tranches' est fourni dans data, la répartition existante est
        entièrement remplacée par la nouvelle liste (toujours au moins 1
        tranche), et doit correspondre au montant_verse final.
        """
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

            if 'tranches' in data:
                lignes, total_affecte = PaiementService._construire_lignes_tranches(
                    data['tranches'] or []
                )

                if total_affecte != paiement.montant_verse:
                    raise ValueError(
                        f"La somme des montants affectés aux tranches ({total_affecte}) "
                        f"doit être égale au montant versé ({paiement.montant_verse})"
                    )

                # Remplace entièrement l'ancienne répartition
                paiement.tranches = [
                    PaiementTranche(tranche_paiement_id=tranche_id, montant_affecte=montant_affecte)
                    for tranche_id, montant_affecte in lignes
                ]

            elif 'montant_verse' in data:
                # Le montant a changé sans nouvelle répartition fournie :
                # on vérifie que l'ancienne répartition reste cohérente.
                if Decimal(str(paiement.montant_alloue)) != paiement.montant_verse:
                    raise ValueError(
                        "Le nouveau montant versé ne correspond plus à la répartition actuelle "
                        "des tranches ; veuillez fournir une nouvelle répartition ('tranches')"
                    )

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
    def get_situation_financiere(inscription_id, annee_scolaire_id, classe_id):
        """
        Récapitulatif de la situation financière d'un élève (inscription) pour
        une année scolaire et une classe données (les tranches étant désormais
        propres à une classe).

        Pour chaque tranche de la classe/année: montant attendu, total versé
        (somme des allocations PaiementTranche), solde restant et statut
        ('Impayé', 'Partiel', 'Soldé'), ainsi que les totaux généraux.

        Args:
            inscription_id: ID de l'inscription de l'élève
            annee_scolaire_id: ID de l'année scolaire
            classe_id: ID de la classe (les tranches dépendent de la classe)

        Returns:
            dict: détail par tranche + totaux (montant attendu, versé, solde global)
        """
        tranches = TranchePaiement.query.filter_by(
            annee_scolaire_id=annee_scolaire_id,
            classe_id=classe_id
        ).order_by(TranchePaiement.date_limite).all()

        detail = []
        total_attendu = Decimal('0')
        total_verse = Decimal('0')

        for tranche in tranches:
            lignes_allouees = db.session.query(PaiementTranche).join(Paiement).filter(
                Paiement.inscription_id == inscription_id,
                PaiementTranche.tranche_paiement_id == tranche.id
            ).all()

            verse_tranche = sum((pt.montant_affecte for pt in lignes_allouees), Decimal('0'))
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
            'classe_id': classe_id,
            'tranches': detail,
            'total_attendu': float(total_attendu),
            'total_verse': float(total_verse),
            'solde_global': float(total_attendu - total_verse)
        }