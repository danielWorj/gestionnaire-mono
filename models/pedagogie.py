from models import db
from models.structure import AnneeScolaire, Classe  # <-- on réutilise les modèles définis dans structure.py
from sqlalchemy.orm import relationship
from datetime import datetime


class Enseignant(db.Model):
    __tablename__ = 'enseignant'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(150), unique=True, nullable=False)
    grade = db.Column(db.String(50))
    est_titulaire = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    titulaires_classe = db.relationship('TitulaireClasse', backref='enseignant', lazy=True, cascade='all, delete-orphan')
    matieres_classe = db.relationship('MatiereClasse', backref='enseignant', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'telephone': self.telephone,
            'email': self.email,
            'grade': self.grade,
            'est_titulaire': self.est_titulaire,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class GroupeMatiere(db.Model):
    __tablename__ = 'groupe_matiere'

    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(150), nullable=False)  # Ex: "Mathématiques"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    matieres = db.relationship('Matiere', backref='groupe_matiere', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'libelle': self.libelle,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Matiere(db.Model):
    __tablename__ = 'matiere'

    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(150), nullable=False)
    groupe_id = db.Column(db.Integer, db.ForeignKey('groupe_matiere.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('libelle', 'groupe_id', name='uq_matiere_groupe'),
    )

    # Relationships
    matieres_classe = db.relationship('MatiereClasse', backref='matiere', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'libelle': self.libelle,
            'groupe_id': self.groupe_id,
            'groupe': self.groupe_matiere.to_dict() if self.groupe_matiere else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TitulaireClasse(db.Model):
    __tablename__ = 'titulaire_classe'

    id = db.Column(db.Integer, primary_key=True)
    classe_id = db.Column(db.Integer, db.ForeignKey('classe.id'), nullable=False)
    enseignant_id = db.Column(db.Integer, db.ForeignKey('enseignant.id'), nullable=False)
    annee_scolaire_id = db.Column(db.Integer, db.ForeignKey('annee_scolaire.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('classe_id', 'annee_scolaire_id', name='uq_titulaire_classe_annee'),
    )

    # Relationships explicites vers Classe et AnneeScolaire (définis dans structure.py)
    classe = db.relationship('Classe', backref=db.backref('titulaires', lazy=True, cascade='all, delete-orphan'))
    annee_scolaire = db.relationship('AnneeScolaire', backref=db.backref('titulaires_classe', lazy=True, cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'classe_id': self.classe_id,
            'classe': self.classe.to_dict() if self.classe else None,
            'enseignant_id': self.enseignant_id,
            'enseignant': self.enseignant.to_dict() if self.enseignant else None,
            'annee_scolaire_id': self.annee_scolaire_id,
            'annee_scolaire': self.annee_scolaire.to_dict() if self.annee_scolaire else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MatiereClasse(db.Model):
    __tablename__ = 'matiere_classe'

    id = db.Column(db.Integer, primary_key=True)
    classe_id = db.Column(db.Integer, db.ForeignKey('classe.id'), nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matiere.id'), nullable=False)
    enseignant_id = db.Column(db.Integer, db.ForeignKey('enseignant.id'), nullable=False)
    coefficient = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('classe_id', 'matiere_id', name='uq_matiere_classe'),
    )

    # Relationship explicite vers Classe (définie dans structure.py)
    classe = db.relationship('Classe', backref=db.backref('matieres_classe', lazy=True, cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'classe_id': self.classe_id,
            'classe': self.classe.to_dict() if self.classe else None,
            'matiere_id': self.matiere_id,
            'matiere': self.matiere.to_dict() if self.matiere else None,
            'enseignant_id': self.enseignant_id,
            'enseignant': self.enseignant.to_dict() if self.enseignant else None,
            'coefficient': self.coefficient,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }