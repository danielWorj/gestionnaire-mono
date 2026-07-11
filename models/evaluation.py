from models import db
from datetime import datetime
from sqlalchemy import CheckConstraint, UniqueConstraint

class Note(db.Model):
    """
    Modèle représentant une note d'un élève pour une matière donnée lors d'une séquence.
    """
    __tablename__ = 'note'
    
    id = db.Column(db.Integer, primary_key=True)
    inscription_id = db.Column(db.Integer, db.ForeignKey('inscription.id'), nullable=False)
    matiere_classe_id = db.Column(db.Integer, db.ForeignKey('matiere_classe.id'), nullable=False)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequence.id'), nullable=False)
    valeur = db.Column(db.Numeric(5, 2), nullable=False)
    absent = db.Column(db.Boolean, default=False, nullable=False)
    saisie_le = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Contraintes
    __table_args__ = (
        UniqueConstraint('inscription_id', 'matiere_classe_id', 'sequence_id', 
                        name='uq_note_inscription_matiere_sequence'),
        CheckConstraint('valeur >= 0 AND valeur <= 20', 
                       name='ck_note_valeur_range'),
    )
    
    # Relations
    inscription = db.relationship('Inscription', backref='notes')
    matiere_classe = db.relationship('MatiereClasse', backref='notes')
    sequence = db.relationship('Sequence', backref='notes')
    
    def to_dict(self):
        return {
            'id': self.id,
            'inscription_id': self.inscription_id,
            'matiere_classe_id': self.matiere_classe_id,
            'sequence_id': self.sequence_id,
            'valeur': float(self.valeur) if self.valeur else None,
            'absent': self.absent,
            'saisie_le': self.saisie_le.isoformat() if self.saisie_le else None
        }


class Discipline(db.Model):
    """
    Modèle représentant les données de discipline (absences, retards, exclusions) 
    pour un élève lors d'une séquence.
    """
    __tablename__ = 'discipline'
    
    id = db.Column(db.Integer, primary_key=True)
    inscription_id = db.Column(db.Integer, db.ForeignKey('inscription.id'), nullable=False)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequence.id'), nullable=False)
    absences_justifiees = db.Column(db.Integer, default=0, nullable=False)
    absences_non_justifiees = db.Column(db.Integer, default=0, nullable=False)
    retards = db.Column(db.Integer, default=0, nullable=False)
    exclusions = db.Column(db.Integer, default=0, nullable=False)
    observation = db.Column(db.Text, nullable=True)
    
    # Contrainte d'unicité
    __table_args__ = (
        UniqueConstraint('inscription_id', 'sequence_id', 
                        name='uq_discipline_inscription_sequence'),
    )
    
    # Relations
    inscription = db.relationship('Inscription', backref='disciplines')
    sequence = db.relationship('Sequence', backref='disciplines')
    
    def to_dict(self):
        return {
            'id': self.id,
            'inscription_id': self.inscription_id,
            'sequence_id': self.sequence_id,
            'absences_justifiees': self.absences_justifiees,
            'absences_non_justifiees': self.absences_non_justifiees,
            'retards': self.retards,
            'exclusions': self.exclusions,
            'observation': self.observation
        }