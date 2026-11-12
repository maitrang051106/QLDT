"""drop tuition installments

Bá» cÆ¡ cháº¿ chia Ä‘á»£t ná»™p há»c phÃ­: má»—i hÃ³a Ä‘Æ¡n thanh toÃ¡n má»™t láº§n duy nháº¥t.

Revision ID: b7e2d41c8a90
Revises: 59f6bf2ad986
Create Date: 2026-11-11 17:30:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "b7e2d41c8a90"
down_revision = "59f6bf2ad986"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("TUITION_PAYMENTS") as batch_op:
        batch_op.drop_constraint(
            "fk_TUITION_PAYMENTS_installment_id_TUITION_INSTALLMENTS", type_="foreignkey"
        )
        batch_op.drop_column("installment_id")
    op.drop_table("TUITION_INSTALLMENTS")


def downgrade() -> None:
    op.create_table(
        "TUITION_INSTALLMENTS",
        sa.Column(
            "installment_id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "semester_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("installment_order", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("percentage", sa.Numeric(5, 2), nullable=True),
        sa.Column(
            "fixed_amount", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=True
        ),
        sa.CheckConstraint(
            "installment_order > 0", name="ck_TUITION_INSTALLMENTS_installment_order_positive"
        ),
        sa.ForeignKeyConstraint(
            ["semester_id"],
            ["SEMESTERS.semester_id"],
            name="fk_TUITION_INSTALLMENTS_semester_id_SEMESTERS",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("installment_id", name="pk_TUITION_INSTALLMENTS"),
        sa.UniqueConstraint(
            "semester_id", "installment_order", name="uq_installment_semester_order"
        ),
    )
    with op.batch_alter_table("TUITION_PAYMENTS") as batch_op:
        batch_op.add_column(
            sa.Column(
                "installment_id",
                sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                nullable=True,
            )
        )
        batch_op.create_foreign_key(
            "fk_TUITION_PAYMENTS_installment_id_TUITION_INSTALLMENTS",
            "TUITION_INSTALLMENTS",
            ["installment_id"],
            ["installment_id"],
            ondelete="RESTRICT",
        )
