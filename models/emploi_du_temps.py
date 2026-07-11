from models import db
from models.pedagogie import MatiereClasse
from models.structure import AnneeScolaire
from sqlalchemy.orm import validates
from datetime import time

class CreneauHoraire(db.Model):
    __tablename__ = 'creneau_horaire'
    
    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(50), nullable=False)  # Ex: "07:30-09:00"
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)
    ordre = db.Column(db.Integer, nullable=False, unique=True)  # Ordre d'affichage
    
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # Relationships
    horaires = db.relationship('Horaire', backref='creneau_horaire', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'libelle': self.libelle,
            'heure_debut': self.heure_debut.isoformat() if self.heure_debut else None,
            'heure_fin': self.heure_fin.isoformat() if self.heure_fin else None,
            'ordre': self.ordre,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Horaire(db.Model):
    __tablename__ = 'horaire'
    
    id = db.Column(db.Integer, primary_key=True)
    matiere_classe_id = db.Column(db.Integer, db.ForeignKey('matiere_classe.id'), nullable=False)
    annee_scolaire_id = db.Column(db.Integer, db.ForeignKey('annee_scolaire.id'), nullable=False)
    jour_semaine = db.Column(db.String(10), nullable=False)
    creneau_id = db.Column(db.Integer, db.ForeignKey('creneau_horaire.id'), nullable=False)
  
    
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint(
            jour_semaine.in_(['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']),
            name='ck_horaire_jour'
        ),
        db.UniqueConstraint(
            'matiere_classe_id', 'jour_semaine', 'creneau_id', 'annee_scolaire_id',
            name='uq_horaire_matiere_classe_creneau'
        ),
    )
    
    # Relationships explicites
    matiere_classe = db.relationship('MatiereClasse', backref=db.backref('horaires', lazy=True))
    annee_scolaire = db.relationship('AnneeScolaire', backref=db.backref('horaires', lazy=True))
    
    @validates('jour_semaine')
    def validate_jour_semaine(self, key, jour):
        jours_valides = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
        if jour not in jours_valides:
            raise ValueError(f"Jour invalide. Doit être l'un de: {', '.join(jours_valides)}")
        return jour
    
    def to_dict(self):
        return {
            'id': self.id,
            'matiere_classe_id': self.matiere_classe_id,
            'matiere_classe': self.matiere_classe.to_dict() if self.matiere_classe else None,
            'annee_scolaire_id': self.annee_scolaire_id,
            'annee_scolaire': self.annee_scolaire.to_dict() if self.annee_scolaire else None,
            'jour_semaine': self.jour_semaine,
            'creneau_id': self.creneau_id,
            'creneau_horaire': self.creneau_horaire.to_dict() if self.creneau_horaire else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }