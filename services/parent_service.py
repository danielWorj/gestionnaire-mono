from models.parent import Parent
from models import db
from sqlalchemy.exc import IntegrityError


class ParentService:
    """Service pour la gestion des parents"""

    @staticmethod
    def get_all():
        return Parent.query.order_by(Parent.nom, Parent.prenom).all()

    @staticmethod
    def get_by_id(id):
        return Parent.query.get(id)

    @staticmethod
    def create(data):
        try:
            parent = Parent(
                nom=data['nom'],
                prenom=data['prenom'],
                telephone=data.get('telephone'),
                email=data.get('email'),
                adresse=data.get('adresse'),
                profession=data.get('profession')
            )
            db.session.add(parent)
            db.session.commit()
            return parent
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Erreur de création du parent: {str(e)}")

    @staticmethod
    def update(id, data):
        parent = Parent.query.get(id)
        if not parent:
            return None

        try:
            if 'nom' in data:
                parent.nom = data['nom']
            if 'prenom' in data:
                parent.prenom = data['prenom']
            if 'telephone' in data:
                parent.telephone = data['telephone']
            if 'email' in data:
                parent.email = data['email']
            if 'adresse' in data:
                parent.adresse = data['adresse']
            if 'profession' in data:
                parent.profession = data['profession']

            db.session.commit()
            return parent
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Erreur de mise à jour du parent: {str(e)}")

    @staticmethod
    def delete(id):
        parent = Parent.query.get(id)
        if not parent:
            return False

        try:
            db.session.delete(parent)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Impossible de supprimer ce parent (des élèves lui sont encore rattachés)")