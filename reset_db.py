"""
Script de réinitialisation complète de la base SQLite.
Recrée toutes les tables à partir des modèles actuels (models/*.py),
sans dépendre des anciennes migrations Alembic.

Usage : python reset_db.py
"""
from app import create_app
from models import db
from sqlalchemy import inspect

app = create_app('development')

with app.app_context():
    db.create_all()
    insp = inspect(db.engine)
    tables = insp.get_table_names()
    print("Base recréée avec succès :", app.config['SQLALCHEMY_DATABASE_URI'])
    print(f"{len(tables)} tables créées :")
    for t in sorted(tables):
        print("  -", t)