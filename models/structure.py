from models import db
from sqlalchemy.orm import relationship
from datetime import date


class Etablissement(db.Model):
    """Établissement scolaire - entité autonome (une seule ligne)"""
    __tablename__ = 'etablissement'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    nom_bilingue = db.Column(db.String(150))  # Nom en anglais
    adresse = db.Column(db.String(255))
    bp = db.Column(db.String(50))
    telephone = db.Column(db.String(20))
    region = db.Column(db.String(100))
    logo_url = db.Column(db.String(255))
    code_acces_hash = db.Column(db.String(255))  # Pour l'authentification
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'nom_bilingue': self.nom_bilingue,
            'adresse': self.adresse,
            'bp': self.bp,
            'telephone': self.telephone,
            'region': self.region,
            'logo_url': self.logo_url
        }


class AnneeScolaire(db.Model):
    """Année scolaire"""
    __tablename__ = 'annee_scolaire'
    
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=False)
    libelle = db.Column(db.String(20), nullable=False)  # Ex: "2025-2026"
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)
    
    # Relations
    trimestres = db.relationship('Trimestre', backref='annee_scolaire', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('libelle', name='uq_annee_libelle'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'libelle': self.libelle,
            'active': self.active,
            'date_debut': self.date_debut.isoformat() if self.date_debut else None,
            'date_fin': self.date_fin.isoformat() if self.date_fin else None,
            'nombre_trimestres': len(self.trimestres)
        }


class Trimestre(db.Model):
    """Trimestre d'une année scolaire"""
    __tablename__ = 'trimestre'
    
    id = db.Column(db.Integer, primary_key=True)
    annee_scolaire_id = db.Column(db.Integer, db.ForeignKey('annee_scolaire.id'), nullable=False)
    libelle = db.Column(db.String(20), nullable=False)  # Ex: "Trimestre 1"
    numero = db.Column(db.Integer, nullable=False)  # 1, 2, ou 3
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)
    
    # Relations
    sequences = db.relationship('Sequence', backref='trimestre', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('annee_scolaire_id', 'numero', name='uq_trimestre_annee_numero'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'libelle': self.libelle,
            'numero': self.numero,
            'date_debut': self.date_debut.isoformat() if self.date_debut else None,
            'date_fin': self.date_fin.isoformat() if self.date_fin else None,
            'annee_scolaire_id': self.annee_scolaire_id,
            'nombre_sequences': len(self.sequences)
        }


class Sequence(db.Model):
    """Séquence d'évaluation (2 par trimestre)"""
    __tablename__ = 'sequence'
    
    id = db.Column(db.Integer, primary_key=True)
    trimestre_id = db.Column(db.Integer, db.ForeignKey('trimestre.id'), nullable=False)
    libelle = db.Column(db.String(10), nullable=False)  # Ex: "SEQ1"
    numero = db.Column(db.Integer, nullable=False)  # 1 ou 2
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)
    
    __table_args__ = (
        db.UniqueConstraint('trimestre_id', 'numero', name='uq_sequence_trimestre_numero'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'libelle': self.libelle,
            'numero': self.numero,
            'date_debut': self.date_debut.isoformat() if self.date_debut else None,
            'date_fin': self.date_fin.isoformat() if self.date_fin else None,
            'trimestre_id': self.trimestre_id
        }


class Cycle(db.Model):
    """Cycle d'enseignement (Collège, Lycée)"""
    __tablename__ = 'cycle'
    
    id = db.Column(db.Integer, primary_key=True)
    ordre = db.Column(db.Integer, nullable=False)  # Ordre de progression
    libelle = db.Column(db.String(50), nullable=False)  # Ex: "Collège"
    cycle = db.Column(db.String(50))  # Description détaillée
    
    # Relations
    classes = db.relationship('Classe', backref='cycle', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'ordre': self.ordre,
            'libelle': self.libelle,
            'cycle': self.cycle,
            'nombre_classes': len(self.classes)
        }


class Classe(db.Model):
    """Classe scolaire"""
    __tablename__ = 'classe'
    
    id = db.Column(db.Integer, primary_key=True)
    cycle_id = db.Column(db.Integer, db.ForeignKey('cycle.id'), nullable=False)
    effectif = db.Column(db.Integer, default=0)
    option = db.Column(db.String(50))  # Ex: "Espagnol I", "Anglais"
    salle = db.Column(db.String(30))
    libelle = db.Column(db.String(50), nullable=False)  # Ex: "6ème A"
    
    def to_dict(self):
        return {
            'id': self.id,
            'libelle': self.libelle,
            'effectif': self.effectif,
            'option': self.option,
            'salle': self.salle,
            'cycle_id': self.cycle_id,
            'cycle_libelle': self.cycle.libelle if self.cycle else None
        }