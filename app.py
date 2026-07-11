from flask import Flask, app, render_template
from config import config
from models import db
from api.structure_api import structure_bp
from api.pedagogie_api import pedagogie_bp
from api.emploi_du_temps_api import emploi_du_temps_bp
from api.inscription_api import inscription_bp
from api.parent_api import parent_bp
from api.evaluation_api import evaluation_bp
from api.paiements_api import paiements_bp

from pathlib import Path
import os

# Dossier contenant ce fichier app.py (fiable, quel que soit l'endroit d'où on lance le script)
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / 'static'
TEMPLATES_DIR = STATIC_DIR / 'templates'


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    app = Flask(
        __name__,
        template_folder=str(TEMPLATES_DIR),
        static_folder=str(STATIC_DIR)
    )
    app.config.from_object(config[config_name])

    # Initialiser les extensions
    db.init_app(app)

    # Enregistrer les blueprints
    app.register_blueprint(structure_bp)
    app.register_blueprint(pedagogie_bp)
    app.register_blueprint(emploi_du_temps_bp)
    app.register_blueprint(inscription_bp)
    app.register_blueprint(parent_bp)
    app.register_blueprint(evaluation_bp)
    app.register_blueprint(paiements_bp)

    # Route de test
    @app.route('/health')
    def health():
        return {'status': 'ok', 'message': 'API Structure Scolaire est opérationnelle'}

    # Route de diagnostic : montre exactement ce que Flask voit sur le disque
    @app.route('/debug-paths')
    def debug_paths():
        templates_exists = TEMPLATES_DIR.exists()
        files_found = []
        if templates_exists:
            files_found = [f.name for f in TEMPLATES_DIR.iterdir()]
        return {
            'BASE_DIR': str(BASE_DIR),
            'TEMPLATES_DIR': str(TEMPLATES_DIR),
            'templates_dir_exists': templates_exists,
            'fichiers_dans_templates': files_found
        }

    # Routes pour servir les pages HTML (templates)
    
    @app.route('/config')
    def config_page():
        return render_template('config.html')

    @app.route('/enseignant')
    def enseignant_page():
        return render_template('enseignant.html')

    @app.route('/matiere')
    def matiere_page():
        return render_template('matiere.html')
    
    @app.route('/horaire')
    def horaire_page():
        return render_template('horaire.html')
    @app.route('/inscription')
    def inscription_page():
        return render_template('inscription.html')
    @app.route('/evaluation')
    def evaluation_page():
        return render_template('evaluation.html')
    @app.route('/paiements')
    def paiements_page():
        return render_template('paiements.html')
    @app.route('/parent')
    def parent_page():
        return render_template('parent.html')
    @app.route('/')
    @app.route('/index')
    def index_page():
        return render_template('index.html')

    # Créer les tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)