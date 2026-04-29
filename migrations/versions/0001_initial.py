"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-29
"""

from typing import Optional, Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Optional[str] = None
branch_labels: Optional[Union[str, Sequence[str]]] = None
depends_on: Optional[Union[str, Sequence[str]]] = None


def upgrade() -> None:
    op.create_table(
        "professional_licenses",
        sa.Column("license_id", sa.String(length=36), nullable=False),
        sa.Column("source_state", sa.String(length=2), nullable=False),
        sa.Column("source_agency", sa.String(length=200), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_record_id", sa.String(length=120), nullable=False),
        sa.Column("license_number", sa.String(length=80), nullable=False),
        sa.Column("license_type_code", sa.String(length=30), nullable=False),
        sa.Column("profession", sa.String(length=120), nullable=False),
        sa.Column("specialty", sa.String(length=160), nullable=True),
        sa.Column("full_name", sa.String(length=240), nullable=False),
        sa.Column("business_name", sa.String(length=240), nullable=True),
        sa.Column("status_raw", sa.String(length=120), nullable=False),
        sa.Column(
            "status_normalized",
            sa.Enum("active", "expired", "suspended", "revoked", "pending", "unknown", name="licensestatus"),
            nullable=False,
        ),
        sa.Column("issue_date", sa.Date(), nullable=True),
        sa.Column("expiration_date", sa.Date(), nullable=False),
        sa.Column("renewal_window_days", sa.Integer(), nullable=False),
        sa.Column("renewal_window_bucket", sa.String(length=30), nullable=False),
        sa.Column("address_city", sa.String(length=120), nullable=True),
        sa.Column("address_state", sa.String(length=2), nullable=True),
        sa.Column("address_zip", sa.String(length=20), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("record_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("license_id"),
        sa.UniqueConstraint(
            "source_state",
            "license_type_code",
            "license_number",
            name="uq_license_state_type_number",
        ),
    )
    op.create_index("idx_license_core_filter", "professional_licenses", ["profession", "source_state", "expiration_date"])
    op.create_index("idx_license_location", "professional_licenses", ["source_state", "address_city", "address_zip"])
    op.create_index("idx_license_renewal_bucket", "professional_licenses", ["renewal_window_bucket", "source_state", "profession"])
    op.create_index("idx_license_status_exp", "professional_licenses", ["status_normalized", "expiration_date"])
    op.create_index("idx_license_type_state_exp", "professional_licenses", ["license_type_code", "source_state", "expiration_date"])

    op.create_table(
        "renewal_monitors",
        sa.Column("monitor_id", sa.String(length=36), nullable=False),
        sa.Column("account_id", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("filters", sa.JSON(), nullable=False),
        sa.Column("window_days", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("monitor_id"),
    )
    op.create_index(op.f("ix_renewal_monitors_account_id"), "renewal_monitors", ["account_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_renewal_monitors_account_id"), table_name="renewal_monitors")
    op.drop_table("renewal_monitors")
    op.drop_index("idx_license_type_state_exp", table_name="professional_licenses")
    op.drop_index("idx_license_status_exp", table_name="professional_licenses")
    op.drop_index("idx_license_renewal_bucket", table_name="professional_licenses")
    op.drop_index("idx_license_location", table_name="professional_licenses")
    op.drop_index("idx_license_core_filter", table_name="professional_licenses")
    op.drop_table("professional_licenses")
