"""add comodos column

Revision ID: add_comodos_column
Revises: 
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_comodos_column'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('imoveis', sa.Column('comodos', sa.Integer))

def downgrade():
    op.drop_column('imoveis', 'comodos') 