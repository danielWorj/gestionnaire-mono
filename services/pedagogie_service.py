from models.pedagogie import (
    Enseignant, GroupeMatiere, Matiere, TitulaireClasse, MatiereClasse
)
from models import db
from sqlalchemy.exc import IntegrityError

class EnseignantService:

    @staticmethod
    def get_all():
        return Enseignant.query.order_by(Enseignant.nom, Enseignant.prenom).all()

    @staticmethod
    def get_by_id(id):
        return Enseignant.query.get(id)

    @staticmethod
    def create(data):
        try:
            enseignant = Enseignant(
                nom=data['nom'],
                prenom=data['prenom'],
                email=data['email'],
                telephone=data.get('telephone'),
                grade=data.get('grade'),
                est_titulaire=data.get('est_titulaire', False)
            )
            db.session.add(enseignant)
            db.session.commit()
            return enseignant
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Un enseignant avec cet email existe déjà")

    @staticmethod
    def update(id, data):
        enseignant = Enseignant.query.get(id)
        if not enseignant:
            return None

        try:
            if 'nom' in data:
                enseignant.nom = data['nom']
            if 'prenom' in data:
                enseignant.prenom = data['prenom']
            if 'email' in data:
                enseignant.email = data['email']
            if 'telephone' in data:
                enseignant.telephone = data['telephone']
            if 'grade' in data:
                enseignant.grade = data['grade']
            if 'est_titulaire' in data:
                enseignant.est_titulaire = data['est_titulaire']

            db.session.commit()
            return enseignant
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Erreur de mise à jour de l'enseignant (email peut-être déjà utilisé)")

    @staticmethod
    def delete(id):
        enseignant = Enseignant.query.get(id)
        if not enseignant:
            return False

        try:
            db.session.delete(enseignant)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Impossible de supprimer cet enseignant (données liées existantes)")


# ==================== GROUPE MATIÈRE ====================

class GroupeMatiereService:

    @staticmethod
    def get_all():
        return GroupeMatiere.query.order_by(GroupeMatiere.libelle).all()

    @staticmethod
    def get_by_id(id):
        return GroupeMatiere.query.get(id)

    @staticmethod
    def create(data):
        groupe = GroupeMatiere(
            libelle=data['libelle'],
        )
        db.session.add(groupe)
        db.session.commit()
        return groupe

    @staticmethod
    def update(id, data):
        groupe = GroupeMatiere.query.get(id)
        if not groupe:
            return None

        if 'libelle' in data:
            groupe.libelle = data['libelle']

        db.session.commit()
        return groupe

    @staticmethod
    def delete(id):
        groupe = GroupeMatiere.query.get(id)
        if not groupe:
            return False

        try:
            db.session.delete(groupe)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Impossible de supprimer ce groupe (matières liées existantes)")


# ==================== MATIÈRE ====================

class MatiereService:

    @staticmethod
    def get_all():
        return Matiere.query.order_by(Matiere.libelle).all()

    @staticmethod
    def get_by_id(id):
        return Matiere.query.get(id)

    @staticmethod
    def get_by_groupe(groupe_id):
        return Matiere.query.filter_by(groupe_id=groupe_id).all()

    @staticmethod
    def create(data):
        try:
            matiere = Matiere(
                libelle=data['libelle'],
                groupe_id=data['groupe_id'],
            )
            db.session.add(matiere)
            db.session.commit()
            return matiere
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Cette matière existe déjà dans ce groupe")

    @staticmethod
    def update(id, data):
        matiere = Matiere.query.get(id)
        if not matiere:
            return None

        try:
            if 'libelle' in data:
                matiere.libelle = data['libelle']
            if 'groupe_id' in data:
                matiere.groupe_id = data['groupe_id']
          

            db.session.commit()
            return matiere
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Erreur de mise à jour de la matière")

    @staticmethod
    def delete(id):
        matiere = Matiere.query.get(id)
        if not matiere:
            return False

        try:
            db.session.delete(matiere)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Impossible de supprimer cette matière (données liées existantes)")


# ==================== TITULAIRE CLASSE ====================

class TitulaireClasseService:

    @staticmethod
    def get_all():
        return TitulaireClasse.query.all()

    @staticmethod
    def get_by_id(id):
        return TitulaireClasse.query.get(id)

    @staticmethod
    def get_by_classe_annee(classe_id, annee_scolaire_id):
        return TitulaireClasse.query.filter_by(
            classe_id=classe_id,
            annee_scolaire_id=annee_scolaire_id
        ).first()

    @staticmethod
    def create(data):
        try:
            existing = TitulaireClasse.query.filter_by(
                classe_id=data['classe_id'],
                annee_scolaire_id=data['annee_scolaire_id']
            ).first()

            if existing:
                raise ValueError("Un titulaire est déjà affecté à cette classe pour cette année")

            titulaire = TitulaireClasse(
                classe_id=data['classe_id'],
                enseignant_id=data['enseignant_id'],
                annee_scolaire_id=data['annee_scolaire_id']
            )
            db.session.add(titulaire)
            db.session.commit()
            return titulaire
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Erreur lors de l'affectation du titulaire")

    @staticmethod
    def update(id, data):
        titulaire = TitulaireClasse.query.get(id)
        if not titulaire:
            return None

        try:
            if 'classe_id' in data:
                titulaire.classe_id = data['classe_id']
            if 'enseignant_id' in data:
                titulaire.enseignant_id = data['enseignant_id']
            if 'annee_scolaire_id' in data:
                titulaire.annee_scolaire_id = data['annee_scolaire_id']

            db.session.commit()
            return titulaire
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Erreur de mise à jour du titulaire")

    @staticmethod
    def delete(id):
        titulaire = TitulaireClasse.query.get(id)
        if not titulaire:
            return False

        db.session.delete(titulaire)
        db.session.commit()
        return True


# ==================== MATIÈRE CLASSE ====================

class MatiereClasseService:

    @staticmethod
    def get_all():
        return MatiereClasse.query.all()

    @staticmethod
    def get_by_id(id):
        return MatiereClasse.query.get(id)

    @staticmethod
    def get_by_classe(classe_id):
        return MatiereClasse.query.filter_by(classe_id=classe_id).all()

    @staticmethod
    def get_by_classe_matiere(classe_id, matiere_id):
        return MatiereClasse.query.filter_by(
            classe_id=classe_id,
            matiere_id=matiere_id
        ).first()

    @staticmethod
    def create(data):
        try:
            existing = MatiereClasse.query.filter_by(
                classe_id=data['classe_id'],
                matiere_id=data['matiere_id']
            ).first()

            if existing:
                raise ValueError("Cette matière est déjà affectée à cette classe")

            matiere_classe = MatiereClasse(
                classe_id=data['classe_id'],
                matiere_id=data['matiere_id'],
                enseignant_id=data['enseignant_id'],
                coefficient=data.get('coefficient', 1)
            )
            db.session.add(matiere_classe)
            db.session.commit()
            return matiere_classe
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Erreur lors de l'affectation de la matière à la classe")

    @staticmethod
    def update(id, data):
        matiere_classe = MatiereClasse.query.get(id)
        if not matiere_classe:
            return None

        try:
            if 'classe_id' in data:
                matiere_classe.classe_id = data['classe_id']
            if 'matiere_id' in data:
                matiere_classe.matiere_id = data['matiere_id']
            if 'enseignant_id' in data:
                matiere_classe.enseignant_id = data['enseignant_id']
            if 'coefficient' in data:
                matiere_classe.coefficient = data['coefficient']

            db.session.commit()
            return matiere_classe
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Erreur de mise à jour de l'affectation matière-classe")

    @staticmethod
    def delete(id):
        matiere_classe = MatiereClasse.query.get(id)
        if not matiere_classe:
            return False

        db.session.delete(matiere_classe)
        db.session.commit()
        return True