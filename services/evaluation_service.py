from models.evaluation import Note, Discipline
from models import db
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from decimal import Decimal, InvalidOperation


class NoteService:
    """Service pour la gestion des notes."""
    
    @staticmethod
    def get_all():
        """Récupérer toutes les notes."""
        return Note.query.all()
    
    @staticmethod
    def get_by_id(note_id):
        """Récupérer une note par son ID."""
        return Note.query.get(note_id)
    
    @staticmethod
    def get_by_inscription_matiere_sequence(inscription_id, matiere_classe_id, sequence_id):
        """Récupérer une note spécifique par ses clés étrangères."""
        return Note.query.filter_by(
            inscription_id=inscription_id,
            matiere_classe_id=matiere_classe_id,
            sequence_id=sequence_id
        ).first()
    
    @staticmethod
    def get_by_sequence(sequence_id):
        """Récupérer toutes les notes d'une séquence."""
        return Note.query.filter_by(sequence_id=sequence_id).all()
    
    @staticmethod
    def get_by_inscription(inscription_id):
        """Récupérer toutes les notes d'un élève (inscription)."""
        return Note.query.filter_by(inscription_id=inscription_id).all()
    
    @staticmethod
    def get_by_classe_matiere_sequence(classe_id, matiere_id, sequence_id):
        """Récupérer les notes d'une classe pour une matière et une séquence données."""
        from models.pedagogie import MatiereClasse
        from models.inscription import Inscription
        
        notes = db.session.query(Note).join(
            Inscription, Note.inscription_id == Inscription.id
        ).join(
            MatiereClasse, Note.matiere_classe_id == MatiereClasse.id
        ).filter(
            Inscription.classe_id == classe_id,
            MatiereClasse.matiere_id == matiere_id,
            Note.sequence_id == sequence_id
        ).all()
        
        return notes
    
    @staticmethod
    def create(data):
        """
        Créer une nouvelle note.
        
        Args:
            data: Dictionnaire contenant inscription_id, matiere_classe_id, 
                  sequence_id, valeur, et optionnellement absent
        """
        try:
            # Validation de la valeur
            try:
                valeur = Decimal(str(data.get('valeur', 0)))
            except (InvalidOperation, TypeError):
                raise ValueError("La valeur de la note doit être un nombre valide")

            if valeur < 0 or valeur > 20:
                raise ValueError("La note doit être comprise entre 0 et 20")
            
            # Vérifier si une note existe déjà pour ce triplet
            existing = Note.query.filter_by(
                inscription_id=data['inscription_id'],
                matiere_classe_id=data['matiere_classe_id'],
                sequence_id=data['sequence_id']
            ).first()
            
            if existing:
                raise ValueError("Une note existe déjà pour cet élève, cette matière et cette séquence")
            
            note = Note(
                inscription_id=data['inscription_id'],
                matiere_classe_id=data['matiere_classe_id'],
                sequence_id=data['sequence_id'],
                valeur=valeur,
                absent=data.get('absent', False),
                saisie_le=datetime.utcnow()
            )
            
            db.session.add(note)
            db.session.commit()
            return note
            
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Erreur lors de la création de la note (contrainte d'intégrité)")
    
    @staticmethod
    def update(note_id, data):
        """
        Mettre à jour une note existante.
        
        Args:
            note_id: ID de la note à mettre à jour
            data: Dictionnaire contenant les champs à mettre à jour
        """
        note = Note.query.get(note_id)
        if not note:
            return None
        
        try:
            if 'valeur' in data:
                try:
                    valeur = Decimal(str(data['valeur']))
                except (InvalidOperation, TypeError):
                    raise ValueError("La valeur de la note doit être un nombre valide")

                if valeur < 0 or valeur > 20:
                    raise ValueError("La note doit être comprise entre 0 et 20")
                note.valeur = valeur
            
            if 'absent' in data:
                note.absent = data['absent']
            
            note.saisie_le = datetime.utcnow()
            
            db.session.commit()
            return note
            
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Erreur lors de la mise à jour de la note")
    
    @staticmethod
    def delete(note_id):
        """Supprimer une note."""
        note = Note.query.get(note_id)
        if not note:
            return False
        
        try:
            db.session.delete(note)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Impossible de supprimer cette note (données liées existantes)")
    
    @staticmethod
    def calculate_moyenne_matiere(inscription_id, matiere_classe_id):
        """
        Calculer la moyenne d'un élève pour une matière donnée.
        
        Args:
            inscription_id: ID de l'inscription de l'élève
            matiere_classe_id: ID de la matière-classe
        
        Returns:
            float: Moyenne de la matière ou None si aucune note
        """
        notes = Note.query.filter_by(
            inscription_id=inscription_id,
            matiere_classe_id=matiere_classe_id
        ).all()
        
        if not notes:
            return None
        
        total = Decimal('0')
        count = 0
        
        for note in notes:
            if note.absent:
                # Note absente compte pour 0
                total += Decimal('0')
            else:
                total += note.valeur
            count += 1
        
        return float(total / count) if count > 0 else None


class DisciplineService:
    """Service pour la gestion de la discipline."""
    
    @staticmethod
    def get_all():
        """Récupérer tous les enregistrements de discipline."""
        return Discipline.query.all()
    
    @staticmethod
    def get_by_id(discipline_id):
        """Récupérer un enregistrement de discipline par son ID."""
        return Discipline.query.get(discipline_id)
    
    @staticmethod
    def get_by_inscription_sequence(inscription_id, sequence_id):
        """Récupérer la discipline pour un élève et une séquence donnés."""
        return Discipline.query.filter_by(
            inscription_id=inscription_id,
            sequence_id=sequence_id
        ).first()
    
    @staticmethod
    def get_by_sequence(sequence_id):
        """Récupérer toutes les données de discipline d'une séquence."""
        return Discipline.query.filter_by(sequence_id=sequence_id).all()
    
    @staticmethod
    def get_by_inscription(inscription_id):
        """Récupérer toutes les données de discipline d'un élève."""
        return Discipline.query.filter_by(inscription_id=inscription_id).all()
    
    @staticmethod
    def create(data):
        """
        Créer un nouvel enregistrement de discipline.
        
        Args:
            data: Dictionnaire contenant inscription_id, sequence_id, et les 
                  données de discipline (absences, retards, etc.)
        """
        try:
            # Vérifier si un enregistrement existe déjà
            existing = Discipline.query.filter_by(
                inscription_id=data['inscription_id'],
                sequence_id=data['sequence_id']
            ).first()
            
            if existing:
                raise ValueError("Un enregistrement de discipline existe déjà pour cet élève et cette séquence")
            
            discipline = Discipline(
                inscription_id=data['inscription_id'],
                sequence_id=data['sequence_id'],
                absences_justifiees=data.get('absences_justifiees', 0),
                absences_non_justifiees=data.get('absences_non_justifiees', 0),
                retards=data.get('retards', 0),
                exclusions=data.get('exclusions', 0),
                observation=data.get('observation')
            )
            
            db.session.add(discipline)
            db.session.commit()
            return discipline
            
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Erreur lors de la création de l'enregistrement de discipline")
    
    @staticmethod
    def update(discipline_id, data):
        """
        Mettre à jour un enregistrement de discipline.
        
        Args:
            discipline_id: ID de l'enregistrement à mettre à jour
            data: Dictionnaire contenant les champs à mettre à jour
        """
        discipline = Discipline.query.get(discipline_id)
        if not discipline:
            return None
        
        try:
            if 'absences_justifiees' in data:
                discipline.absences_justifiees = data['absences_justifiees']
            
            if 'absences_non_justifiees' in data:
                discipline.absences_non_justifiees = data['absences_non_justifiees']
            
            if 'retards' in data:
                discipline.retards = data['retards']
            
            if 'exclusions' in data:
                discipline.exclusions = data['exclusions']
            
            if 'observation' in data:
                discipline.observation = data['observation']
            
            db.session.commit()
            return discipline
            
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Erreur lors de la mise à jour de la discipline")
    
    @staticmethod
    def delete(discipline_id):
        """Supprimer un enregistrement de discipline."""
        discipline = Discipline.query.get(discipline_id)
        if not discipline:
            return False
        
        try:
            db.session.delete(discipline)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Impossible de supprimer cet enregistrement de discipline")
    
    @staticmethod
    def get_aggregation_by_trimestre(inscription_id, trimestre_id):
        """
        Agréger les données de discipline pour un trimestre.
        
        Args:
            inscription_id: ID de l'inscription de l'élève
            trimestre_id: ID du trimestre
        
        Returns:
            dict: Totaux des absences, retards, exclusions pour le trimestre
        """
        from models.structure import Sequence
        
        # Récupérer les séquences du trimestre
        sequences = Sequence.query.filter_by(trimestre_id=trimestre_id).all()
        sequence_ids = [s.id for s in sequences]
        
        # Récupérer les données de discipline pour ces séquences
        disciplines = Discipline.query.filter(
            Discipline.inscription_id == inscription_id,
            Discipline.sequence_id.in_(sequence_ids)
        ).all()
        
        # Agrégation
        total_justifiees = sum(d.absences_justifiees for d in disciplines)
        total_non_justifiees = sum(d.absences_non_justifiees for d in disciplines)
        total_retards = sum(d.retards for d in disciplines)
        total_exclusions = sum(d.exclusions for d in disciplines)
        
        # Concaténation des observations
        observations = [d.observation for d in disciplines if d.observation]
        
        return {
            'absences_justifiees': total_justifiees,
            'absences_non_justifiees': total_non_justifiees,
            'retards': total_retards,
            'exclusions': total_exclusions,
            'observations': ' | '.join(observations) if observations else None
        }
    
    @staticmethod
    def get_aggregation_by_annee(inscription_id, annee_scolaire_id):
        """
        Agréger les données de discipline pour une année scolaire.
        
        Args:
            inscription_id: ID de l'inscription de l'élève
            annee_scolaire_id: ID de l'année scolaire
        
        Returns:
            dict: Totaux des absences, retards, exclusions pour l'année
        """
        from models.structure import Sequence, Trimestre
        
        # Récupérer les trimestres de l'année
        trimestres = Trimestre.query.filter_by(annee_scolaire_id=annee_scolaire_id).all()
        trimestre_ids = [t.id for t in trimestres]
        
        # Récupérer toutes les séquences de ces trimestres
        sequences = Sequence.query.filter(
            Sequence.trimestre_id.in_(trimestre_ids)
        ).all()
        sequence_ids = [s.id for s in sequences]
        
        # Récupérer les données de discipline
        disciplines = Discipline.query.filter(
            Discipline.inscription_id == inscription_id,
            Discipline.sequence_id.in_(sequence_ids)
        ).all()
        
        # Agrégation
        total_justifiees = sum(d.absences_justifiees for d in disciplines)
        total_non_justifiees = sum(d.absences_non_justifiees for d in disciplines)
        total_retards = sum(d.retards for d in disciplines)
        total_exclusions = sum(d.exclusions for d in disciplines)
        
        # Concaténation des observations
        observations = [d.observation for d in disciplines if d.observation]
        
        return {
            'absences_justifiees': total_justifiees,
            'absences_non_justifiees': total_non_justifiees,
            'retards': total_retards,
            'exclusions': total_exclusions,
            'observations': ' | '.join(observations) if observations else None
        }