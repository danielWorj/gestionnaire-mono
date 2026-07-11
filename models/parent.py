from models import db
from datetime import datetime


class Parent(db.Model):
    __tablename__ = 'parent'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(150))
    adresse = db.Column(db.String(255))
    profession = db.Column(db.String(150))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Un parent peut avoir plusieurs enfants (élèves).
    # backref='parent' crée automatiquement Eleve.parent
    eleves = db.relationship('Eleve', backref='parent', lazy=True)

    def to_dict(self, with_eleves=False):
        data = {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'telephone': self.telephone,
            'email': self.email,
            'adresse': self.adresse,
            'profession': self.profession,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if with_eleves:
            data['eleves'] = [eleve.to_dict(with_parent=False) for eleve in self.eleves]
        return data