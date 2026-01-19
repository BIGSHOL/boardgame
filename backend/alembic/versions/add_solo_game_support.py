"""Add solo game support

Make lobby_id nullable and remove FK constraints that block AI players.

Revision ID: add_solo_game_support
Revises: e6a12178d39b
Create Date: 2026-01-19
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_solo_game_support'
down_revision = 'e6a12178d39b'
branch_labels = None
depends_on = None


def upgrade():
    # Make lobby_id nullable for solo games
    op.alter_column('games', 'lobby_id',
                    existing_type=sa.INTEGER(),
                    nullable=True)

    # Drop the foreign key constraint on current_turn_player_id
    # This allows AI players with negative IDs
    op.drop_constraint('games_current_turn_player_id_fkey', 'games', type_='foreignkey')

    # Drop the foreign key constraint on game_actions.player_id
    # This allows recording actions from AI players with negative IDs
    op.drop_constraint('game_actions_player_id_fkey', 'game_actions', type_='foreignkey')


def downgrade():
    # Restore foreign key constraint on game_actions
    op.create_foreign_key('game_actions_player_id_fkey', 'game_actions', 'users',
                          ['player_id'], ['id'])

    # Restore foreign key constraint on games
    op.create_foreign_key('games_current_turn_player_id_fkey', 'games', 'users',
                          ['current_turn_player_id'], ['id'])

    # Make lobby_id not nullable again
    op.alter_column('games', 'lobby_id',
                    existing_type=sa.INTEGER(),
                    nullable=False)
