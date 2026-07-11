from models import db
from models.structure import Classe, AnneeScolaire
from sqlalchemy.orm import validates
from datetime import datetime


class Eleve(db.Model):
    __tablename__ = 'eleve'

    id = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.String(30), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date)
    lieu_naissance = db.Column(db.String(150))
    sexe = db.Column(db.String(1))  # 'M' ou 'F'
    adresse = db.Column(db.String(255))
    photo_url = db.Column(db.String(255))  # chemin relatif (ex: storage/eleves/xxx.jpg)

    # Chaque élève appartient à un parent
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint(sexe.in_(['M', 'F']), name='ck_eleve_sexe'),
    )

    # Relationships
    inscriptions = db.relationship('Inscription', backref='eleve', lazy=True, cascade='all, delete-orphan')
    # NB: la relation 'parent' (Eleve.parent) est créée automatiquement
    # par le backref défini dans models/parent.py (Parent.eleves)

    @validates('sexe')
    def validate_sexe(self, key, value):
        if value is not None and value not in ['M', 'F']:
            raise ValueError("Sexe invalide. Doit être 'M' ou 'F'")
        return value

    def to_dict(self, with_parent=True):
        data = {
            'id': self.id,
            'matricule': self.matricule,
            'nom': self.nom,
            'prenom': self.prenom,
            'date_naissance': self.date_naissance.isoformat() if self.date_naissance else None,
            'lieu_naissance': self.lieu_naissance,
            'sexe': self.sexe,
            'adresse': self.adresse,
            'photo_url': self.photo_url,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if with_parent and self.parent:
            data['parent'] = self.parent.to_dict()
        return data


class Inscription(db.Model):
    __tablename__ = 'inscription'

    STATUTS_VALIDES = ['Inscrit', 'Redoublant', 'Transfere', 'Abandon']

    id = db.Column(db.Integer, primary_key=True)
    eleve_id = db.Column(db.Integer, db.ForeignKey('eleve.id'), nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classe.id'), nullable=False)
    annee_scolaire_id = db.Column(db.Integer, db.ForeignKey('annee_scolaire.id'), nullable=False)
    date_inscription = db.Column(db.Date, default=datetime.utcnow)
    statut = db.Column(db.String(20), default='Inscrit', nullable=False)
    redoublant = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('eleve_id', 'annee_scolaire_id', name='uq_inscription_eleve_annee'),
        db.CheckConstraint(statut.in_(STATUTS_VALIDES), name='ck_inscription_statut'),
    )

    # Relationships explicites vers Classe et AnneeScolaire (définis dans structure.py)
    classe = db.relationship('Classe', backref=db.backref('inscriptions', lazy=True))
    annee_scolaire = db.relationship('AnneeScolaire', backref=db.backref('inscriptions', lazy=True, cascade='all, delete-orphan'))

    @validates('statut')
    def validate_statut(self, key, statut):
        if statut not in self.STATUTS_VALIDES:
            raise ValueError(f"Statut invalide. Doit être l'un de: {', '.join(self.STATUTS_VALIDES)}")
        return statut

    def to_dict(self):
        return {
            'id': self.id,
            'eleve_id': self.eleve_id,
            'eleve': self.eleve.to_dict() if self.eleve else None,
            'classe_id': self.classe_id,
            'classe': self.classe.to_dict() if self.classe else None,
            'annee_scolaire_id': self.annee_scolaire_id,
            'annee_scolaire': self.annee_scolaire.to_dict() if self.annee_scolaire else None,
            'date_inscription': self.date_inscription.isoformat() if self.date_inscription else None,
            'statut': self.statut,
            'redoublant': self.redoublant,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }