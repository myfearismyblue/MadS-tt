"""add content

Revision ID: 7e17ba85aea2
Revises: 42dafb0cad6c
Create Date: 2024-06-23 14:59:48.169091

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e17ba85aea2'
down_revision: Union[str, None] = '42dafb0cad6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('memes', sa.Column('content', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('memes', 'content')
    # ### end Alembic commands ###
