"""Add database constraints - UNIQUE and CHECK

Revision ID: add_constraints
Revises: initial
Create Date: 2026-03-24 08:32:21.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_constraints"
down_revision: Union[str, None] = "initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ==================== UNIQUE constraints ====================
    
    # api_token.token уже имеет unique индекс из initial миграции
    # Добавляем UNIQUE на llm_models.name
    op.create_unique_constraint("uq_llm_models_name", "llm_models", ["name"])
    
    # ==================== CHECK constraints ====================
    
    # Chat settings: temperature (0.0-2.0)
    op.create_check_constraint(
        "chk_chat_settings_temperature",
        "chat_settings",
        "temperature IS NULL OR (temperature >= 0.0 AND temperature <= 2.0)"
    )
    
    # Chat settings: max_tokens (1-32768)
    op.create_check_constraint(
        "chk_chat_settings_max_tokens",
        "chat_settings",
        "max_tokens IS NULL OR (max_tokens >= 1 AND max_tokens <= 32768)"
    )
    
    # Chat settings: context_window (512-131072)
    op.create_check_constraint(
        "chk_chat_settings_context_window",
        "chat_settings",
        "context_window IS NULL OR (context_window >= 512 AND context_window <= 131072)"
    )
    
    # LLM models: temperature (0.0-2.0)
    op.create_check_constraint(
        "chk_llm_models_temperature",
        "llm_models",
        "temperature IS NULL OR (temperature >= 0.0 AND temperature <= 2.0)"
    )
    
    # LLM models: max_tokens (1-32768)
    op.create_check_constraint(
        "chk_llm_models_max_tokens",
        "llm_models",
        "max_tokens IS NULL OR (max_tokens >= 1 AND max_tokens <= 32768)"
    )
    
    # LLM models: context_window (512-131072)
    op.create_check_constraint(
        "chk_llm_models_context_window",
        "llm_models",
        "context_window IS NULL OR (context_window >= 512 AND context_window <= 131072)"
    )


def downgrade() -> None:
    # ==================== Remove CHECK constraints ====================
    
    op.drop_constraint("chk_llm_models_context_window", "llm_models", type_="check")
    op.drop_constraint("chk_llm_models_max_tokens", "llm_models", type_="check")
    op.drop_constraint("chk_llm_models_temperature", "llm_models", type_="check")
    
    op.drop_constraint("chk_chat_settings_context_window", "chat_settings", type_="check")
    op.drop_constraint("chk_chat_settings_max_tokens", "chat_settings", type_="check")
    op.drop_constraint("chk_chat_settings_temperature", "chat_settings", type_="check")
    
    # ==================== Remove UNIQUE constraints ====================
    
    op.drop_constraint("uq_llm_models_name", "llm_models", type_="unique")
