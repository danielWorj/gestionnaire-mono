import os
import uuid
from pathlib import Path
from datetime import datetime, date

from models.inscription import Eleve, Inscription
from models.parent import Parent
from models import db
from sqlalchemy.exc import IntegrityError


def _parse_date(valeur):
    """
    Convertit une date reçue du client (string 'YYYY-MM-DD' venant d'un
    formulaire HTML/multipart, ou déjà un objet date/datetime venant du JSON)
    en objet Python `date`, seul type accepté par la colonne SQLite.
    Retourne None si la valeur est vide/absente.
    """
    if not valeur:
        return None
    if isinstance(valeur, datetime):
        return valeur.date()
    if isinstance(valeur, date):
        return valeur
    if isinstance(valeur, str):
        valeur = valeur.strip()
        if not valeur:
            return None
        try:
            # Format natif des <input type="date"> : YYYY-MM-DD
            return datetime.strptime(valeur, '%Y-%m-%d').date()
        except ValueError:
            try:
                # Repli si jamais une valeur ISO avec heure est envoyée
                return datetime.fromisoformat(valeur).date()
            except ValueError:
                raise ValueError(f"Format de date invalide : '{valeur}' (attendu : AAAA-MM-JJ)")
    raise ValueError(f"Format de date invalide : {valeur!r}")


# ==================== UPLOAD PHOTO ====================

# services/ -> racine du projet (APP/)
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / 'storage' / 'eleves'
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

EXTENSIONS_AUTORISEES = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def _extension_autorisee(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSIONS_AUTORISEES


def _sauvegarder_photo(file_storage):
    """Sauvegarde le fichier uploadé dans storage/eleves et retourne le chemin relatif à stocker en BDD."""
    if file_storage is None or file_storage.filename == '':
        return None

    if not _extension_autorisee(file_storage.filename):
        raise ValueError(
            f"Format de photo non autorisé. Formats acceptés: {', '.join(EXTENSIONS_AUTORISEES)}"
        )

    extension = file_storage.filename.rsplit('.', 1)[1].lower()
    nom_fichier = f"{uuid.uuid4().hex}.{extension}"
    chemin_absolu = STORAGE_DIR / nom_fichier
    file_storage.save(str(chemin_absolu))

    # Chemin relatif stocké en base (ex: storage/eleves/xxxxx.jpg)
    return str(Path('storage') / 'eleves' / nom_fichier)


def _supprimer_photo(chemin_relatif):
    """Supprime un fichier photo du disque à partir de son chemin relatif stocké en BDD."""
    if not chemin_relatif:
        return
    chemin_absolu = BASE_DIR / chemin_relatif
    try:
        if chemin_absolu.is_file():
            os.remove(str(chemin_absolu))
    except OSError:
        pass


# ==================== ELEVE ====================

class EleveService:
    """Service pour la gestion des élèves"""

    @staticmethod
    def get_all():
        return Eleve.query.order_by(Eleve.nom, Eleve.prenom).all()

    @staticmethod
    def get_by_id(id):
        return Eleve.query.get(id)

    @staticmethod
    def get_by_matricule(matricule):
        return Eleve.query.filter_by(matricule=matricule).first()

    @staticmethod
    def _resoudre_parent(data):
        """Retourne un parent_id valide: soit un parent existant, soit un parent créé à la volée."""
        if data.get('parent_id'):
            parent = Parent.query.get(data['parent_id'])
            if not parent:
                raise ValueError("Le parent indiqué (parent_id) n'existe pas")
            return parent.id

        # Création d'un nouveau parent à partir des champs fournis
        if data.get('parent_nom') and data.get('parent_prenom'):
            parent = Parent(
                nom=data['parent_nom'],
                prenom=data['parent_prenom'],
                telephone=data.get('parent_telephone'),
                email=data.get('parent_email'),
                adresse=data.get('parent_adresse'),
                profession=data.get('parent_profession')
            )
            db.session.add(parent)
            db.session.flush()  # récupère parent.id sans commit définitif
            return parent.id

        raise ValueError(
            "Un parent est requis: fournir 'parent_id' (parent existant) "
            "ou 'parent_nom' + 'parent_prenom' (nouveau parent)"
        )

    @staticmethod
    def create(data, photo_file=None):
        try:
            if Eleve.query.filter_by(matricule=data['matricule']).first():
                raise ValueError("Un élève avec ce matricule existe déjà")

            parent_id = EleveService._resoudre_parent(data)
            photo_url = _sauvegarder_photo(photo_file)

            eleve = Eleve(
                matricule=data['matricule'],
                nom=data['nom'],
                prenom=data['prenom'],
                date_naissance=_parse_date(data.get('date_naissance')),
                lieu_naissance=data.get('lieu_naissance'),
                sexe=data.get('sexe'),
                adresse=data.get('adresse'),
                photo_url=photo_url,
                parent_id=parent_id
            )
            db.session.add(eleve)
            db.session.commit()
            return eleve
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Erreur de création de l'élève: {str(e)}")
        except ValueError:
            db.session.rollback()
            raise

    @staticmethod
    def update(id, data, photo_file=None):
        eleve = Eleve.query.get(id)
        if not eleve:
            return None

        try:
            if 'matricule' in data and data['matricule'] != eleve.matricule:
                if Eleve.query.filter_by(matricule=data['matricule']).first():
                    raise ValueError("Un élève avec ce matricule existe déjà")
                eleve.matricule = data['matricule']
            if 'nom' in data:
                eleve.nom = data['nom']
            if 'prenom' in data:
                eleve.prenom = data['prenom']
            if 'date_naissance' in data:
                eleve.date_naissance = _parse_date(data['date_naissance'])
            if 'lieu_naissance' in data:
                eleve.lieu_naissance = data['lieu_naissance']
            if 'sexe' in data:
                eleve.sexe = data['sexe']
            if 'adresse' in data:
                eleve.adresse = data['adresse']
            if data.get('parent_id') or (data.get('parent_nom') and data.get('parent_prenom')):
                eleve.parent_id = EleveService._resoudre_parent(data)

            if photo_file is not None and photo_file.filename != '':
                nouvelle_photo = _sauvegarder_photo(photo_file)
                ancienne_photo = eleve.photo_url
                eleve.photo_url = nouvelle_photo
                _supprimer_photo(ancienne_photo)

            db.session.commit()
            return eleve
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Erreur de mise à jour de l'élève: {str(e)}")
        except ValueError:
            db.session.rollback()
            raise

    @staticmethod
    def delete(id):
        eleve = Eleve.query.get(id)
        if not eleve:
            return False

        try:
            photo_url = eleve.photo_url
            db.session.delete(eleve)
            db.session.commit()
            _supprimer_photo(photo_url)
            return True
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Impossible de supprimer cet élève (inscriptions liées existantes)")


# ==================== INSCRIPTION ====================

class InscriptionService:
    """Service pour la gestion des inscriptions"""

    @staticmethod
    def get_all():
        return Inscription.query.all()

    @staticmethod
    def get_by_id(id):
        return Inscription.query.get(id)

    @staticmethod
    def get_by_classe_annee(classe_id, annee_scolaire_id):
        """Récupère la liste des élèves inscrits dans une classe pour une année"""
        return Inscription.query.filter_by(
            classe_id=classe_id,
            annee_scolaire_id=annee_scolaire_id
        ).all()

    @staticmethod
    def get_by_annee(annee_scolaire_id):
        """Récupère toutes les inscriptions d'une année scolaire"""
        return Inscription.query.filter_by(annee_scolaire_id=annee_scolaire_id).all()

    @staticmethod
    def get_historique_eleve(eleve_id):
        """Récupère l'historique des inscriptions d'un élève (toutes années)"""
        return Inscription.query.filter_by(eleve_id=eleve_id).order_by(
            Inscription.annee_scolaire_id.desc()
        ).all()

    @staticmethod
    def get_inscription_active(eleve_id, annee_scolaire_id):
        """Récupère l'inscription d'un élève pour une année donnée"""
        return Inscription.query.filter_by(
            eleve_id=eleve_id,
            annee_scolaire_id=annee_scolaire_id
        ).first()

    @staticmethod
    def create(data):
        """Créer une nouvelle inscription (un élève ne peut être inscrit qu'une fois par année)"""
        try:
            existing = Inscription.query.filter_by(
                eleve_id=data['eleve_id'],
                annee_scolaire_id=data['annee_scolaire_id']
            ).first()
            if existing:
                raise ValueError("Cet élève est déjà inscrit pour cette année scolaire")

            inscription = Inscription(
                eleve_id=data['eleve_id'],
                classe_id=data['classe_id'],
                annee_scolaire_id=data['annee_scolaire_id'],
                date_inscription=_parse_date(data.get('date_inscription')),
                statut=data.get('statut', 'Inscrit'),
                redoublant=data.get('redoublant', False)
            )
            db.session.add(inscription)
            db.session.commit()
            return inscription
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Erreur lors de l'inscription: {str(e)}")

    @staticmethod
    def update(id, data):
        """Mettre à jour une inscription"""
        inscription = Inscription.query.get(id)
        if not inscription:
            return None

        try:
            if 'classe_id' in data:
                inscription.classe_id = data['classe_id']
            if 'annee_scolaire_id' in data:
                inscription.annee_scolaire_id = data['annee_scolaire_id']
            if 'date_inscription' in data:
                inscription.date_inscription = _parse_date(data['date_inscription'])
            if 'statut' in data:
                inscription.statut = data['statut']
            if 'redoublant' in data:
                inscription.redoublant = data['redoublant']

            db.session.commit()
            return inscription
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Erreur de mise à jour de l'inscription: {str(e)}")

    @staticmethod
    def transferer_classe(id, nouvelle_classe_id):
        """Transférer un élève vers une autre classe, même année scolaire"""
        inscription = Inscription.query.get(id)
        if not inscription:
            return None

        inscription.classe_id = nouvelle_classe_id
        db.session.commit()
        return inscription

    @staticmethod
    def delete(id):
        """Supprimer une inscription"""
        inscription = Inscription.query.get(id)
        if not inscription:
            return False

        try:
            db.session.delete(inscription)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Erreur de suppression de l'inscription")