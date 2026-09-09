"""Ajout de classe_id sur tranche_paiement

Revision ID: 30dcbacb1fd4
Revises: bcccc52c0f57
Create Date: 2026-09-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30dcbacb1fd4'
down_revision = 'bcccc52c0f57'
branch_labels = None
depends_on = None


def upgrade():
    # NOTE: la table tranche_paiement est vide en production locale au moment
    # de l'écriture de cette migration, donc on peut ajouter la colonne en
    # NOT NULL directement. Si des lignes existent déjà chez vous, il faudra
    # d'abord les backfiller (voir commentaire plus bas) avant d'appliquer
    # cette migration.
    with op.batch_alter_table('tranche_paiement', schema=None) as batch_op:
        batch_op.add_column(sa.Column('classe_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            'fk_tranche_paiement_classe_id', 'classe', ['classe_id'], ['id']
        )
        batch_op.create_unique_constraint(
            'uq_tranche_classe_annee_libelle',
            ['classe_id', 'annee_scolaire_id', 'libelle'],
        )

    # Si vous avez déjà des données à conserver, remplacez le bloc ci-dessus par :
    #
    # with op.batch_alter_table('tranche_paiement', schema=None) as batch_op:
    #     batch_op.add_column(sa.Column('classe_id', sa.Integer(), nullable=True))
    #
    # op.execute("UPDATE tranche_paiement SET classe_id = <valeur_par_defaut>")
    #
    # with op.batch_alter_table('tranche_paiement', schema=None) as batch_op:
    #     batch_op.alter_column('classe_id', nullable=False)
    #     batch_op.create_foreign_key(
    #         'fk_tranche_paiement_classe_id', 'classe', ['classe_id'], ['id']
    #     )
    #     batch_op.create_unique_constraint(
    #         'uq_tranche_classe_annee_libelle',
    #         ['classe_id', 'annee_scolaire_id', 'libelle'],
    #     )


def downgrade():
    with op.batch_alter_table('tranche_paiement', schema=None) as batch_op:
        batch_op.drop_constraint('uq_tranche_classe_annee_libelle', type_='unique')
        batch_op.drop_constraint('fk_tranche_paiement_classe_id', type_='foreignkey')
        batch_op.drop_column('classe_id')
