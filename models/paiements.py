from models import db
from sqlalchemy.orm import validates
from datetime import datetime


class TranchePaiement(db.Model):
    """Tranche de paiement (échéance) rattachée à une année scolaire ET à une classe.

    Les montants attendus peuvent différer d'une classe à l'autre pour une même
    année scolaire (ex: frais différents entre le Collège et le Lycée), d'où
    l'ajout de classe_id.
    """
    __tablename__ = 'tranche_paiement'

    id = db.Column(db.Integer, primary_key=True)
    annee_scolaire_id = db.Column(db.Integer, db.ForeignKey('annee_scolaire.id'), nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classe.id'), nullable=False)
    libelle = db.Column(db.String(100), nullable=False)  # Ex: "1ère tranche"
    montant_attendu = db.Column(db.Numeric(10, 2), nullable=False)
    date_limite = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint('montant_attendu > 0', name='ck_tranche_montant_positif'),
        db.UniqueConstraint('classe_id', 'annee_scolaire_id', 'libelle', name='uq_tranche_classe_annee_libelle'),
    )

    # Relations explicites vers AnneeScolaire et Classe (définies dans structure.py)
    annee_scolaire = db.relationship(
        'AnneeScolaire',
        backref=db.backref('tranches_paiement', lazy=True, cascade='all, delete-orphan')
    )
    classe = db.relationship(
        'Classe',
        backref=db.backref('tranches_paiement', lazy=True, cascade='all, delete-orphan')
    )
    # Lignes d'allocation de paiements pointant vers cette tranche
    paiement_tranches = db.relationship(
        'PaiementTranche', backref='tranche_paiement', lazy=True, cascade='all, delete-orphan'
    )

    @validates('montant_attendu')
    def validate_montant_attendu(self, key, value):
        if value is not None and float(value) <= 0:
            raise ValueError("Le montant attendu doit être positif")
        return value

    def to_dict(self, with_annee=False, with_classe=False):
        data = {
            'id': self.id,
            'annee_scolaire_id': self.annee_scolaire_id,
            'classe_id': self.classe_id,
            'libelle': self.libelle,
            'montant_attendu': float(self.montant_attendu) if self.montant_attendu is not None else None,
            'date_limite': self.date_limite.isoformat() if self.date_limite else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if with_annee and self.annee_scolaire:
            data['annee_scolaire'] = self.annee_scolaire.to_dict()
        if with_classe and self.classe:
            data['classe'] = self.classe.to_dict()
        return data


class Paiement(db.Model):
    """Paiement effectué par un élève (inscription).

    Un paiement n'est pas obligé de couvrir une tranche précise : il peut
    rester totalement ou partiellement non affecté. Quand il est réparti, la
    répartition entre les tranches couvertes est portée par la table
    d'association PaiementTranche. La somme des montants affectés ne peut
    jamais dépasser le montant versé (montant_alloue <= montant_verse).
    """
    __tablename__ = 'paiement'

    id = db.Column(db.Integer, primary_key=True)
    inscription_id = db.Column(db.Integer, db.ForeignKey('inscription.id'), nullable=False)
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

    # Lignes d'allocation vers les tranches couvertes par ce paiement (1..n)
    tranches = db.relationship(
        'PaiementTranche', backref='paiement', lazy=True, cascade='all, delete-orphan'
    )

    @validates('montant_verse')
    def validate_montant_verse(self, key, value):
        if value is not None and float(value) <= 0:
            raise ValueError("Le montant versé doit être positif")
        return value

    @property
    def montant_alloue(self):
        """Somme des montants affectés aux tranches liées à ce paiement."""
        return sum((float(pt.montant_affecte) for pt in self.tranches), 0.0)

    @property
    def montant_non_affecte(self):
        """Part du montant versé qui n'est affectée à aucune tranche (paiement
        libre, ou surplus restant une fois toutes les tranches soldées)."""
        montant_verse = float(self.montant_verse) if self.montant_verse is not None else 0.0
        return max(montant_verse - self.montant_alloue, 0.0)

    def to_dict(self, with_relations=True):
        data = {
            'id': self.id,
            'inscription_id': self.inscription_id,
            'montant_verse': float(self.montant_verse) if self.montant_verse is not None else None,
            'montant_alloue': self.montant_alloue,
            'montant_non_affecte': self.montant_non_affecte,
            'date_paiement': self.date_paiement.isoformat() if self.date_paiement else None,
            'mode_paiement': self.mode_paiement,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'tranches_paiement_id': [pt.tranche_paiement_id for pt in self.tranches],
        }
        if with_relations:
            data['tranches'] = [pt.to_dict() for pt in self.tranches]
            if self.inscription:
                data['eleve'] = self.inscription.eleve.to_dict(with_parent=False) if self.inscription.eleve else None
        return data


class PaiementTranche(db.Model):
    """Table d'association Paiement <-> TranchePaiement.

    Permet à un paiement de couvrir plusieurs tranches (et à une tranche d'être
    alimentée par plusieurs paiements successifs), en conservant le montant
    précisément affecté à chaque tranche.
    """
    __tablename__ = 'paiement_tranche'

    id = db.Column(db.Integer, primary_key=True)
    paiement_id = db.Column(db.Integer, db.ForeignKey('paiement.id'), nullable=False)
    tranche_paiement_id = db.Column(db.Integer, db.ForeignKey('tranche_paiement.id'), nullable=False)
    montant_affecte = db.Column(db.Numeric(10, 2), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('paiement_id', 'tranche_paiement_id', name='uq_paiement_tranche'),
        db.CheckConstraint('montant_affecte > 0', name='ck_paiement_tranche_montant_positif'),
    )

    @validates('montant_affecte')
    def validate_montant_affecte(self, key, value):
        if value is not None and float(value) <= 0:
            raise ValueError("Le montant affecté à une tranche doit être positif")
        return value

    def to_dict(self, with_tranche=True):
        data = {
            'id': self.id,
            'paiement_id': self.paiement_id,
            'tranche_paiement_id': self.tranche_paiement_id,
            'montant_affecte': float(self.montant_affecte) if self.montant_affecte is not None else None,
        }
        if with_tranche and self.tranche_paiement:
            data['tranche_paiement'] = self.tranche_paiement.to_dict()
        return data