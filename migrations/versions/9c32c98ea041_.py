"""empty message

Revision ID: 9c32c98ea041
Revises: cd15610d0f50
Create Date: 2017-05-15 21:47:08.431701

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c32c98ea041'
down_revision = 'cd15610d0f50'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('data_model', sa.Column('longname', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('data_model', 'longname')
    # ### end Alembic commands ###