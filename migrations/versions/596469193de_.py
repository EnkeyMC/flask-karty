"""empty message

Revision ID: 596469193de
Revises: 2f4d1750abe1
Create Date: 2015-04-01 12:28:49.208539

"""

# revision identifiers, used by Alembic.
revision = '596469193de'
down_revision = '2f4d1750abe1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('carddata',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('card_number', sa.String(length=32), nullable=True),
    sa.Column('di_user', sa.Integer(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('id_card_reader', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id', name='pk_carddata')
    )
    op.create_index('ix_carddata_card_number', 'carddata', ['card_number'], unique=False)
    op.create_index('ix_carddata_di_user', 'carddata', ['di_user'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('activate_token', sa.String(length=128), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('verified', sa.Boolean(name='verified'), nullable=False),
    sa.Column('card_number', sa.String(length=32), nullable=True),
    sa.Column('full_name', sa.String(length=40), nullable=True),
    sa.Column('access', sa.String(length=1), nullable=True),
    sa.PrimaryKeyConstraint('id', name='pk_users')
    )
    op.create_index('ix_users_access', 'users', ['access'], unique=False)
    op.create_index('ix_users_card_number', 'users', ['card_number'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_full_name', 'users', ['full_name'], unique=False)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_table('user_password_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(length=128), nullable=False),
    sa.Column('used', sa.Boolean(name='used'), nullable=True),
    sa.Column('expiration_dt', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_password_tokens_user_id_users'),
    sa.PrimaryKeyConstraint('id', name='pk_user_password_tokens')
    )
    op.create_index('ix_user_password_tokens_value', 'user_password_tokens', ['value'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_password_tokens_value', table_name='user_password_tokens')
    op.drop_table('user_password_tokens')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_full_name', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_card_number', table_name='users')
    op.drop_index('ix_users_access', table_name='users')
    op.drop_table('users')
    op.drop_index('ix_carddata_di_user', table_name='carddata')
    op.drop_index('ix_carddata_card_number', table_name='carddata')
    op.drop_table('carddata')
    ### end Alembic commands ###
