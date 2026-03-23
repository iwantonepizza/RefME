"""Initial migration - create all tables

Revision ID: initial
Revises: 
Create Date: 2026-03-03 18:00:00.000000+00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Таблица api_token
    op.create_table(
        "api_token",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_api_token_token"), "api_token", ["token"], unique=True)

    # 2. Таблица llm_models
    op.create_table(
        "llm_models",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("provider_model", sa.String(), nullable=False),
        sa.Column("types", sa.JSON(), nullable=False, server_default='["text"]'),
        sa.Column("provider", sa.String(), nullable=False, default="ollama"),
        sa.Column("active", sa.Boolean(), nullable=False, default=True),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("max_tokens", sa.Integer(), nullable=True),
        sa.Column("context_window", sa.Integer(), nullable=True),
        sa.Column("supported_formats", sa.JSON(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_llm_models_provider_model"), "llm_models", ["provider_model"], unique=True)

    # 3. Таблица chat_settings
    op.create_table(
        "chat_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_id", sa.Integer(), nullable=False),
        sa.Column("model_id", sa.Integer(), nullable=True),
        sa.Column("model_name", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("system_prompt", sa.Text(), nullable=True),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("max_tokens", sa.Integer(), nullable=True),
        sa.Column("context_window", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["token_id"], ["api_token.id"], ),
        sa.ForeignKeyConstraint(["model_id"], ["llm_models.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    # Индексы для ускорения JOIN запросов
    op.create_index(op.f("ix_chat_settings_token_id"), "chat_settings", ["token_id"], unique=False)
    op.create_index(op.f("ix_chat_settings_model_id"), "chat_settings", ["model_id"], unique=False)

    # 4. Таблица chat_sessions
    op.create_table(
        "chat_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_id", sa.String(), nullable=False),
        sa.Column("chat_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["chat_id"], ["chat_settings.id"], ),
        sa.ForeignKeyConstraint(["token_id"], ["api_token.token"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    # Индексы для ускорения поиска
    op.create_index(op.f("ix_chat_sessions_chat_id"), "chat_sessions", ["chat_id"], unique=False)
    op.create_index(op.f("ix_chat_sessions_token_id"), "chat_sessions", ["token_id"], unique=False)

    # 5. Таблица chat_messages
    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, default="pending"),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    # Индекс для ускорения поиска сообщений по сессии
    op.create_index(op.f("ix_chat_messages_session_id"), "chat_messages", ["session_id"], unique=False)


def downgrade() -> None:
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
    op.drop_table("chat_settings")
    op.drop_index(op.f("ix_llm_models_provider_model"), table_name="llm_models")
    op.drop_table("llm_models")
    op.drop_index(op.f("ix_api_token_token"), table_name="api_token")
    op.drop_table("api_token")
