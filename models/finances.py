from models import db
from sqlalchemy.orm import validates
from datetime import datetime


class CategorieEntree(db.Model):
    """Catégorie de classification des entrées (recettes) financières.

    Ex: "Frais de scolarité", "Subvention", "Don", "Autre recette".
    """
    __tablename__ = 'categorie_entree'

    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Entrées rattachées à cette catégorie (définies plus bas dans ce fichier)
    entrees = db.relationship(
        'Entree', backref='categorie_entree', lazy=True, cascade='all, delete-orphan'
    )

    @validates('libelle')
    def validate_libelle(self, key, value):
        if not value or not value.strip():
            raise ValueError("Le libellé de la catégorie d'entrée est obligatoire")
        return value.strip()

    def to_dict(self, with_entrees=False):
        data = {
            'id': self.id,
            'libelle': self.libelle,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if with_entrees:
            data['entrees'] = [e.to_dict(with_categorie=False) for e in self.entrees]
        return data


class Entree(db.Model):
    """Entrée (recette) financière, rattachée à une catégorie d'entrée."""
    __tablename__ = 'entree'

    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    categorie_entree_id = db.Column(db.Integer, db.ForeignKey('categorie_entree.id'), nullable=False)
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint('montant > 0', name='ck_entree_montant_positif'),
    )

    # Sorties financées par cette entrée (relation définie via Sortie.entree_id)
    sorties = db.relationship(
        'Sortie', backref='entree', lazy=True
    )

    @validates('libelle')
    def validate_libelle(self, key, value):
        if not value or not value.strip():
            raise ValueError("Le libellé de l'entrée est obligatoire")
        return value.strip()

    @validates('montant')
    def validate_montant(self, key, value):
        if value is not None and float(value) <= 0:
            raise ValueError("Le montant de l'entrée doit être positif")
        return value

    @property
    def montant_sorti(self):
        """Somme des sorties directement rattachées à cette entrée."""
        return sum((float(s.montant) for s in self.sorties), 0.0)

    @property
    def montant_disponible(self):
        """Solde restant de l'entrée une fois les sorties rattachées déduites."""
        montant = float(self.montant) if self.montant is not None else 0.0
        return montant - self.montant_sorti

    def to_dict(self, with_categorie=True, with_sorties=False):
        data = {
            'id': self.id,
            'libelle': self.libelle,
            'description': self.description,
            'categorie_entree_id': self.categorie_entree_id,
            'montant': float(self.montant) if self.montant is not None else None,
            'date': self.date.isoformat() if self.date else None,
            'montant_sorti': self.montant_sorti,
            'montant_disponible': self.montant_disponible,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if with_categorie and self.categorie_entree:
            data['categorie_entree'] = self.categorie_entree.to_dict()
        if with_sorties:
            data['sorties'] = [s.to_dict(with_categorie=False, with_entree=False) for s in self.sorties]
        return data


class CategorieSortie(db.Model):
    """Catégorie de classification des sorties (dépenses) financières.

    Ex: "Salaire", "Fournitures", "Maintenance", "Autre dépense".
    """
    __tablename__ = 'categorie_sortie'

    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Sorties rattachées à cette catégorie (définies plus bas dans ce fichier)
    sorties = db.relationship(
        'Sortie', backref='categorie_sortie', lazy=True, cascade='all, delete-orphan'
    )

    @validates('libelle')
    def validate_libelle(self, key, value):
        if not value or not value.strip():
            raise ValueError("Le libellé de la catégorie de sortie est obligatoire")
        return value.strip()

    def to_dict(self, with_sorties=False):
        data = {
            'id': self.id,
            'libelle': self.libelle,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if with_sorties:
            data['sorties'] = [s.to_dict(with_categorie=False) for s in self.sorties]
        return data


class Sortie(db.Model):
    """Sortie (dépense) financière, rattachée à une catégorie de sortie et,
    optionnellement, à l'entrée qui la finance (ex: dépense financée par une
    subvention ou un don précis)."""
    __tablename__ = 'sortie'

    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    categorie_sortie_id = db.Column(db.Integer, db.ForeignKey('categorie_sortie.id'), nullable=False)
    entree_id = db.Column(db.Integer, db.ForeignKey('entree.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint('montant > 0', name='ck_sortie_montant_positif'),
    )

    @validates('libelle')
    def validate_libelle(self, key, value):
        if not value or not value.strip():
            raise ValueError("Le libellé de la sortie est obligatoire")
        return value.strip()

    @validates('montant')
    def validate_montant(self, key, value):
        if value is not None and float(value) <= 0:
            raise ValueError("Le montant de la sortie doit être positif")
        return value

    def to_dict(self, with_categorie=True, with_entree=True):
        data = {
            'id': self.id,
            'libelle': self.libelle,
            'description': self.description,
            'montant': float(self.montant) if self.montant is not None else None,
            'date': self.date.isoformat() if self.date else None,
            'categorie_sortie_id': self.categorie_sortie_id,
            'entree_id': self.entree_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if with_categorie and self.categorie_sortie:
            data['categorie_sortie'] = self.categorie_sortie.to_dict()
        if with_entree and self.entree:
            data['entree'] = self.entree.to_dict(with_categorie=False, with_sorties=False)
        return data