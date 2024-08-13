from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, func


# revision identifiers, used by Alembic.
revision = '0d4698bdc67a'
down_revision = 'f957ad8ad06f'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Add tmdb_id column as nullable initially
    with op.batch_alter_table('movies', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tmdb_id', sa.Integer(), nullable=True))

    # Step 2: Backfill tmdb_id with unique values
    # Replace this with your own logic for generating unique tmdb_id values if necessary
    movies_table = table('movies',
                         column('id', sa.Integer),
                         column('tmdb_id', sa.Integer))
    
    # Example update to set tmdb_id to id * 1000 to ensure uniqueness
    op.execute(movies_table.update().where(movies_table.c.tmdb_id.is_(None)).values({'tmdb_id': sa.text("id * 1000")}))

    # Step 3: Make tmdb_id column non-nullable and add unique constraint
    with op.batch_alter_table('movies', schema=None) as batch_op:
        batch_op.alter_column('tmdb_id', nullable=False)
        batch_op.create_unique_constraint(None, ['tmdb_id'])


def downgrade():
    with op.batch_alter_table('movies', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('tmdb_id')
