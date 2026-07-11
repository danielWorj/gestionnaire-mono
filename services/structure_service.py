from models.structure import (
    db, Etablissement, AnneeScolaire, Trimestre, 
    Sequence, Cycle, Classe
)
from datetime import date
from sqlalchemy.exc import IntegrityError


class EtablissementService:
    """Service pour la gestion de l'établissement (configuration unique)"""
    
    @staticmethod
    def get_etablissement():
        """Récupère l'établissement (une seule ligne possible)"""
        return Etablissement.query.first()
    
    @staticmethod
    def create_etablissement(data):
        """Crée l'établissement (une seule fois)"""
        if Etablissement.query.first():
            raise ValueError("L'établissement est déjà configuré")
        
        etablissement = Etablissement(
            nom=data['nom'],
            nom_bilingue=data.get('nom_bilingue'),
            adresse=data.get('adresse'),
            bp=data.get('bp'),
            telephone=data.get('telephone'),
            region=data.get('region'),
            logo_url=data.get('logo_url'),
            code_acces_hash=data.get('code_acces_hash')
        )
        
        db.session.add(etablissement)
        db.session.commit()
        return etablissement
    
    @staticmethod
    def update_etablissement(data):
        """Met à jour les informations de l'établissement"""
        etablissement = Etablissement.query.first()
        if not etablissement:
            raise ValueError("Aucun établissement configuré")
        
        etablissement.nom = data.get('nom', etablissement.nom)
        etablissement.nom_bilingue = data.get('nom_bilingue', etablissement.nom_bilingue)
        etablissement.adresse = data.get('adresse', etablissement.adresse)
        etablissement.bp = data.get('bp', etablissement.bp)
        etablissement.telephone = data.get('telephone', etablissement.telephone)
        etablissement.region = data.get('region', etablissement.region)
        etablissement.logo_url = data.get('logo_url', etablissement.logo_url)
        
        db.session.commit()
        return etablissement


class AnneeScolaireService:
    """Service pour la gestion des années scolaires"""
    
    @staticmethod
    def get_all():
        """Récupère toutes les années scolaires"""
        return AnneeScolaire.query.order_by(AnneeScolaire.libelle.desc()).all()
    
    @staticmethod
    def get_by_id(id):
        """Récupère une année scolaire par ID"""
        return AnneeScolaire.query.get(id)
    
    @staticmethod
    def get_active():
        """Récupère l'année scolaire active"""
        return AnneeScolaire.query.filter_by(active=True).first()
    
    @staticmethod
    def create(data):
        """Crée une nouvelle année scolaire"""
        # Désactiver l'année active précédente si celle-ci est active
        if data.get('active', False):
            AnneeScolaire.query.update({'active': False})
        
        annee = AnneeScolaire(
            libelle=data['libelle'],
            active=data.get('active', False),
            date_debut=data.get('date_debut'),
            date_fin=data.get('date_fin')
        )
        
        db.session.add(annee)
        db.session.commit()
        return annee
    
    @staticmethod
    def update(id, data):
        """Met à jour une année scolaire"""
        annee = AnneeScolaire.query.get(id)
        if not annee:
            raise ValueError("Année scolaire non trouvée")
        
        # Si on active cette année, désactiver les autres
        if data.get('active', False):
            AnneeScolaire.query.update({'active': False})
        
        annee.libelle = data.get('libelle', annee.libelle)
        annee.active = data.get('active', annee.active)
        annee.date_debut = data.get('date_debut', annee.date_debut)
        annee.date_fin = data.get('date_fin', annee.date_fin)
        
        db.session.commit()
        return annee
    
    @staticmethod
    def delete(id):
        """Supprime une année scolaire"""
        annee = AnneeScolaire.query.get(id)
        if not annee:
            raise ValueError("Année scolaire non trouvée")
        
        # Vérifier si des notes existent (à implémenter selon les besoins)
        db.session.delete(annee)
        db.session.commit()
        return True
    
    @staticmethod
    def set_active(id):
        """Active une année scolaire (désactive les autres)"""
        AnneeScolaire.query.update({'active': False})
        annee = AnneeScolaire.query.get(id)
        if annee:
            annee.active = True
            db.session.commit()
        return annee


class TrimestreService:
    """Service pour la gestion des trimestres"""
    
    @staticmethod
    def get_by_annee(annee_id):
        """Récupère tous les trimestres d'une année"""
        return Trimestre.query.filter_by(annee_scolaire_id=annee_id).order_by(Trimestre.numero).all()
    
    @staticmethod
    def get_by_id(id):
        """Récupère un trimestre par ID"""
        return Trimestre.query.get(id)
    
    @staticmethod
    def create(data):
        """Crée un nouveau trimestre"""
        # Vérifier qu'il n'y a pas déjà 3 trimestres pour cette année
        existing = Trimestre.query.filter_by(
            annee_scolaire_id=data['annee_scolaire_id'],
            numero=data['numero']
        ).first()
        
        if existing:
            raise ValueError("Un trimestre avec ce numéro existe déjà pour cette année")
        
        trimestre = Trimestre(
            annee_scolaire_id=data['annee_scolaire_id'],
            libelle=data['libelle'],
            numero=data['numero'],
            date_debut=data.get('date_debut'),
            date_fin=data.get('date_fin')
        )
        
        db.session.add(trimestre)
        db.session.commit()
        return trimestre
    
    @staticmethod
    def update(id, data):
        """Met à jour un trimestre"""
        trimestre = Trimestre.query.get(id)
        if not trimestre:
            raise ValueError("Trimestre non trouvé")
        
        trimestre.libelle = data.get('libelle', trimestre.libelle)
        trimestre.date_debut = data.get('date_debut', trimestre.date_debut)
        trimestre.date_fin = data.get('date_fin', trimestre.date_fin)
        
        db.session.commit()
        return trimestre
    
    @staticmethod
    def delete(id):
        """Supprime un trimestre"""
        trimestre = Trimestre.query.get(id)
        if not trimestre:
            raise ValueError("Trimestre non trouvé")
        
        # Vérifier si des notes existent (à implémenter)
        db.session.delete(trimestre)
        db.session.commit()
        return True


class SequenceService:
    """Service pour la gestion des séquences"""
    
    @staticmethod
    def get_by_trimestre(trimestre_id):
        """Récupère toutes les séquences d'un trimestre"""
        return Sequence.query.filter_by(trimestre_id=trimestre_id).order_by(Sequence.numero).all()
    
    @staticmethod
    def get_by_id(id):
        """Récupère une séquence par ID"""
        return Sequence.query.get(id)
    
    @staticmethod
    def create(data):
        """Crée une nouvelle séquence"""
        # Vérifier qu'il n'y a pas déjà 2 séquences pour ce trimestre
        existing = Sequence.query.filter_by(
            trimestre_id=data['trimestre_id'],
            numero=data['numero']
        ).first()
        
        if existing:
            raise ValueError("Une séquence avec ce numéro existe déjà pour ce trimestre")
        
        sequence = Sequence(
            trimestre_id=data['trimestre_id'],
            libelle=data['libelle'],
            numero=data['numero'],
            date_debut=data.get('date_debut'),
            date_fin=data.get('date_fin')
        )
        
        db.session.add(sequence)
        db.session.commit()
        return sequence
    
    @staticmethod
    def update(id, data):
        """Met à jour une séquence"""
        sequence = Sequence.query.get(id)
        if not sequence:
            raise ValueError("Séquence non trouvée")
        
        sequence.libelle = data.get('libelle', sequence.libelle)
        sequence.date_debut = data.get('date_debut', sequence.date_debut)
        sequence.date_fin = data.get('date_fin', sequence.date_fin)
        
        db.session.commit()
        return sequence
    
    @staticmethod
    def delete(id):
        """Supprime une séquence"""
        sequence = Sequence.query.get(id)
        if not sequence:
            raise ValueError("Séquence non trouvée")
        
        # Vérifier si des notes existent (à implémenter)
        db.session.delete(sequence)
        db.session.commit()
        return True


class CycleService:
    """Service pour la gestion des cycles"""
    
    @staticmethod
    def get_all():
        """Récupère tous les cycles"""
        return Cycle.query.order_by(Cycle.ordre).all()
    
    @staticmethod
    def get_by_id(id):
        """Récupère un cycle par ID"""
        return Cycle.query.get(id)
    
    @staticmethod
    def create(data):
        """Crée un nouveau cycle"""
        cycle = Cycle(
            ordre=data['ordre'],
            libelle=data['libelle'],
            cycle=data.get('cycle')
        )
        
        db.session.add(cycle)
        db.session.commit()
        return cycle
    
    @staticmethod
    def update(id, data):
        """Met à jour un cycle"""
        cycle = Cycle.query.get(id)
        if not cycle:
            raise ValueError("Cycle non trouvé")
        
        cycle.ordre = data.get('ordre', cycle.ordre)
        cycle.libelle = data.get('libelle', cycle.libelle)
        cycle.cycle = data.get('cycle', cycle.cycle)
        
        db.session.commit()
        return cycle
    
    @staticmethod
    def delete(id):
        """Supprime un cycle"""
        cycle = Cycle.query.get(id)
        if not cycle:
            raise ValueError("Cycle non trouvé")
        
        db.session.delete(cycle)
        db.session.commit()
        return True


class ClasseService:
    """Service pour la gestion des classes"""
    
    @staticmethod
    def get_all():
        """Récupère toutes les classes"""
        return Classe.query.order_by(Classe.libelle).all()
    
    @staticmethod
    def get_by_cycle(cycle_id):
        """Récupère les classes d'un cycle"""
        return Classe.query.filter_by(cycle_id=cycle_id).order_by(Classe.libelle).all()
    
    @staticmethod
    def get_by_id(id):
        """Récupère une classe par ID"""
        return Classe.query.get(id)
    
    @staticmethod
    def create(data):
        """Crée une nouvelle classe"""
        classe = Classe(
            libelle=data['libelle'],
            cycle_id=data['cycle_id'],
            effectif=data.get('effectif', 0),
            option=data.get('option'),
            salle=data.get('salle')
        )
        
        db.session.add(classe)
        db.session.commit()
        return classe
    
    @staticmethod
    def update(id, data):
        """Met à jour une classe"""
        classe = Classe.query.get(id)
        if not classe:
            raise ValueError("Classe non trouvée")
        
        classe.libelle = data.get('libelle', classe.libelle)
        classe.cycle_id = data.get('cycle_id', classe.cycle_id)
        classe.effectif = data.get('effectif', classe.effectif)
        classe.option = data.get('option', classe.option)
        classe.salle = data.get('salle', classe.salle)
        
        db.session.commit()
        return classe
    
    @staticmethod
    def delete(id):
        """Supprime une classe"""
        classe = Classe.query.get(id)
        if not classe:
            raise ValueError("Classe non trouvée")
        
        # Vérifier si des inscriptions existent (à implémenter)
        db.session.delete(classe)
        db.session.commit()
        return True