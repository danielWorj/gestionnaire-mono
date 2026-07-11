from models import db
from sqlalchemy.orm import validates
from datetime import datetime


class TranchePaiement(db.Model):
    """Tranche de paiement (échéance) rattachée à une année scolaire"""
    __tablename__ = 'tranche_paiement'

    id = db.Column(db.Integer, primary_key=True)
    annee_scolaire_id = db.Column(db.Integer, db.ForeignKey('annee_scolaire.id'), nullable=False)
    libelle = db.Column(db.String(100), nullable=False)  # Ex: "1ère tranche"
    montant_attendu = db.Column(db.Numeric(10, 2), nullable=False)
    date_limite = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint('montant_attendu > 0', name='ck_tranche_montant_positif'),
    )

    # Relations explicites vers AnneeScolaire (définie dans structure.py)
    annee_scolaire = db.relationship(
        'AnneeScolaire',
        backref=db.backref('tranches_paiement', lazy=True, cascade='all, delete-orphan')
    )
    paiements = db.relationship('Paiement', backref='tranche_paiement', lazy=True, cascade='all, delete-orphan')

    @validates('montant_attendu')
    def validate_montant_attendu(self, key, value):
        if value is not None and float(value) <= 0:
            raise ValueError("Le montant attendu doit être positif")
        return value

    def to_dict(self, with_annee=False):
        data = {
            'id': self.id,
            'annee_scolaire_id': self.annee_scolaire_id,
            'libelle': self.libelle,
            'montant_attendu': float(self.montant_attendu) if self.montant_attendu is not None else None,
            'date_limite': self.date_limite.isoformat() if self.date_limite else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if with_annee and self.annee_scolaire:
            data['annee_scolaire'] = self.annee_scolaire.to_dict()
        return data


class Paiement(db.Model):
    """Paiement effectué par un élève (inscription) pour une tranche de paiement donnée"""
    __tablename__ = 'paiement'

    id = db.Column(db.Integer, primary_key=True)
    inscription_id = db.Column(db.Integer, db.ForeignKey('inscription.id'), nullable=False)
    tranche_paiement_id = db.Column(db.Integer, db.ForeignKey('tranche_paiement.id'), nullable=False)
    montant_verse = db.Column(db.Numeric(10, 2), nullable=False)
    date_paiement = db.Column(db.Date, default=datetime.utcnow)
    mode_paiement = db.Column(db.String(30))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint('montant_verse > 0', name='ck_paiement_montant_positif'),
    )

    # Relation explicite vers Inscription (définie dans inscription.py)
    inscription = db.relationship(
        'Inscription',
        backref=db.backref('paiements', lazy=True, cascade='all, delete-orphan')
    )

    @validates('montant_verse')
    def validate_montant_verse(self, key, value):
        if value is not None and float(value) <= 0:
            raise ValueError("Le montant versé doit être positif")
        return value

    def to_dict(self, with_relations=True):
        data = {
            'id': self.id,
            'inscription_id': self.inscription_id,
            'tranche_paiement_id': self.tranche_paiement_id,
            'montant_verse': float(self.montant_verse) if self.montant_verse is not None else None,
            'date_paiement': self.date_paiement.isoformat() if self.date_paiement else None,
            'mode_paiement': self.mode_paiement,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if with_relations:
            data['tranche_paiement'] = self.tranche_paiement.to_dict() if self.tranche_paiement else None
            if self.inscription:
                data['eleve'] = self.inscription.eleve.to_dict(with_parent=False) if self.inscription.eleve else None
        return data