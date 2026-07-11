from models.emploi_du_temps import CreneauHoraire, Horaire
from models.pedagogie import MatiereClasse
from models import db
from sqlalchemy.exc import IntegrityError
from datetime import time


class CreneauHoraireService:
    """Service pour la gestion des créneaux horaires"""
    
    @staticmethod
    def get_all():
        """Récupérer tous les créneaux horaires"""
        return CreneauHoraire.query.order_by(CreneauHoraire.ordre).all()
    
    @staticmethod
    def get_by_id(id):
        """Récupérer un créneau par ID"""
        return CreneauHoraire.query.get(id)
    
    @staticmethod
    def create(data):
        """Créer un nouveau créneau horaire"""
        try:
            # Vérifier l'unicité de l'ordre
            if CreneauHoraire.query.filter_by(ordre=data['ordre']).first():
                raise ValueError("Un créneau avec cet ordre existe déjà")
            
            creneau = CreneauHoraire(
                libelle=data['libelle'],
                heure_debut=data['heure_debut'],
                heure_fin=data['heure_fin'],
                ordre=data['ordre']
            )
            db.session.add(creneau)
            db.session.commit()
            return creneau
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Erreur de création: {str(e)}")
    
    @staticmethod
    def update(id, data):
        """Mettre à jour un créneau horaire"""
        creneau = CreneauHoraire.query.get(id)
        if not creneau:
            return None
        
        try:
            # Vérifier l'unicité de l'ordre si modifié
            if 'ordre' in data and data['ordre'] != creneau.ordre:
                if CreneauHoraire.query.filter_by(ordre=data['ordre']).first():
                    raise ValueError("Un créneau avec cet ordre existe déjà")
            
            if 'libelle' in data:
                creneau.libelle = data['libelle']
            if 'heure_debut' in data:
                creneau.heure_debut = data['heure_debut']
            if 'heure_fin' in data:
                creneau.heure_fin = data['heure_fin']
            if 'ordre' in data:
                creneau.ordre = data['ordre']
            
            db.session.commit()
            return creneau
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Erreur de mise à jour: {str(e)}")
    
    @staticmethod
    def delete(id):
        """Supprimer un créneau horaire"""
        creneau = CreneauHoraire.query.get(id)
        if not creneau:
            return False
        
        try:
            db.session.delete(creneau)
            db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError("Impossible de supprimer ce créneau (horaires associés existants)")


class HoraireService:
    """Service pour la gestion des horaires (emploi du temps)"""
    
    @staticmethod
    def get_all():
        """Récupérer tous les horaires"""
        return Horaire.query.all()
    
    @staticmethod
    def get_by_id(id):
        """Récupérer un horaire par ID"""
        return Horaire.query.get(id)
    
    @staticmethod
    def get_by_classe_annee(classe_id, annee_scolaire_id):
        """Récupérer tous les horaires d'une classe pour une année scolaire"""
        return Horaire.query.join(MatiereClasse).join(
            CreneauHoraire, Horaire.creneau_id == CreneauHoraire.id
        ).filter(
            MatiereClasse.classe_id == classe_id,
            Horaire.annee_scolaire_id == annee_scolaire_id
        ).order_by(
            Horaire.jour_semaine,
            CreneauHoraire.ordre
        ).all()
    
    @staticmethod
    def get_by_enseignant_annee(enseignant_id, annee_scolaire_id):
        """Récupérer tous les horaires d'un enseignant pour une année scolaire"""
        return Horaire.query.join(MatiereClasse).join(
            CreneauHoraire, Horaire.creneau_id == CreneauHoraire.id
        ).filter(
            MatiereClasse.enseignant_id == enseignant_id,
            Horaire.annee_scolaire_id == annee_scolaire_id
        ).order_by(
            Horaire.jour_semaine,
            CreneauHoraire.ordre
        ).all()
    
    @staticmethod
    def verifier_collision(matiere_classe_id, jour_semaine, creneau_id, annee_scolaire_id, horaire_id=None):
        """
        Vérifier s'il y a une collision (classe ou enseignant déjà occupé)
        Retourne un tuple: (has_collision, message)
        """
        # Récupérer les infos de la matière-classe
        matiere_classe = MatiereClasse.query.get(matiere_classe_id)
        if not matiere_classe:
            return True, "Matière-classe inexistante"
        
        classe_id = matiere_classe.classe_id
        enseignant_id = matiere_classe.enseignant_id
        
        # Requête pour trouver les collisions
        query = Horaire.query.join(MatiereClasse).filter(
            Horaire.annee_scolaire_id == annee_scolaire_id,
            Horaire.jour_semaine == jour_semaine,
            Horaire.creneau_id == creneau_id
        )
        
        # Exclure l'horaire actuel si mise à jour
        if horaire_id:
            query = query.filter(Horaire.id != horaire_id)
        
        conflits = query.all()
        
        for horaire in conflits:
            mc = horaire.matiere_classe
            
            # Collision si même classe
            if mc.classe_id == classe_id:
                return True, f"Collision: La classe est déjà occupée à ce créneau"
            
            # Collision si même enseignant
            if mc.enseignant_id == enseignant_id:
                return True, f"Collision: L'enseignant est déjà occupé à ce créneau"
        
        return False, None
    
    @staticmethod
    def create(data):
        """Créer un nouvel horaire"""
        try:
            # Vérifier les collisions
            has_collision, message = HoraireService.verifier_collision(
                data['matiere_classe_id'],
                data['jour_semaine'],
                data['creneau_id'],
                data['annee_scolaire_id']
            )
            if has_collision:
                raise ValueError(message)
            
            horaire = Horaire(
                matiere_classe_id=data['matiere_classe_id'],
                annee_scolaire_id=data['annee_scolaire_id'],
                jour_semaine=data['jour_semaine'],
                creneau_id=data['creneau_id'],
               
            )
            db.session.add(horaire)
            db.session.commit()
            return horaire
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Erreur de création: {str(e)}")
    
    @staticmethod
    def update(id, data):
        """Mettre à jour un horaire"""
        horaire = Horaire.query.get(id)
        if not horaire:
            return None
        
        try:
            # Si on change le créneau, le jour ou la matière-classe, vérifier les collisions
            if any(key in data for key in ['matiere_classe_id', 'jour_semaine', 'creneau_id']):
                matiere_classe_id = data.get('matiere_classe_id', horaire.matiere_classe_id)
                jour_semaine = data.get('jour_semaine', horaire.jour_semaine)
                creneau_id = data.get('creneau_id', horaire.creneau_id)
                annee_scolaire_id = horaire.annee_scolaire_id
                
                has_collision, message = HoraireService.verifier_collision(
                    matiere_classe_id,
                    jour_semaine,
                    creneau_id,
                    annee_scolaire_id,
                    horaire_id=id
                )
                if has_collision:
                    raise ValueError(message)
            
            if 'matiere_classe_id' in data:
                horaire.matiere_classe_id = data['matiere_classe_id']
            if 'annee_scolaire_id' in data:
                horaire.annee_scolaire_id = data['annee_scolaire_id']
            if 'jour_semaine' in data:
                horaire.jour_semaine = data['jour_semaine']
            if 'creneau_id' in data:
                horaire.creneau_id = data['creneau_id']
       
            
            db.session.commit()
            return horaire
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Erreur de mise à jour: {str(e)}")
    
    @staticmethod
    def delete(id):
        """Supprimer un horaire"""
        horaire = Horaire.query.get(id)
        if not horaire:
            return False
        
        try:
            db.session.delete(horaire)
            db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Erreur de suppression: {str(e)}")
    
    @staticmethod
    def delete_by_filters(classe_id=None, annee_scolaire_id=None, jour_semaine=None):
        """Supprimer plusieurs horaires selon les filtres"""
        query = Horaire.query
        
        if classe_id:
            query = query.join(MatiereClasse).filter(MatiereClasse.classe_id == classe_id)
        if annee_scolaire_id:
            query = query.filter(Horaire.annee_scolaire_id == annee_scolaire_id)
        if jour_semaine:
            query = query.filter(Horaire.jour_semaine == jour_semaine)
        
        horaires = query.all()
        count = len(horaires)
        
        for horaire in horaires:
            db.session.delete(horaire)
        
        db.session.commit()
        return count