"""Add showcase approval status table

Revision ID: 22fe3db8aba8
Revises: 02b006cb222c
Create Date: 2024-07-21 10:49:16.978530

"""
from alembic import op
import sqlalchemy as sa
from ckanext.showcase.data.constants import *

# revision identifiers, used by Alembic.
revision = '22fe3db8aba8'
down_revision = '02b006cb222c'
branch_labels = None
depends_on = None


def upgrade():
    engine = op.get_bind()
    inspector = sa.inspect(engine)
    tables = inspector.get_table_names()
    if "showcase_package_association" not in tables:
        op.create_table(
            "showcase_package_association",
            sa.Column(
                "package_id",
                sa.UnicodeText,
                sa.ForeignKey("package.id", ondelete="CASCADE", onupdate="CASCADE"),
                primary_key=True,
                nullable=False,
            ),
            sa.Column(
                "showcase_id",
                sa.UnicodeText,
                sa.ForeignKey("package.id", ondelete="CASCADE", onupdate="CASCADE"),
                primary_key=True,
                nullable=False,
            ),
        )
    if "showcase_package_association" not in tables:
        op.create_table(
            "showcase_admin",
            sa.Column(
                "user_id",
                sa.UnicodeText,
                sa.ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
                primary_key=True,
                nullable=False,
            ),
        )
    
    if "showcase_approval" not in tables:
        op.create_table(
            "showcase_approval",
            sa.Column(
                "showcase_id",
                sa.UnicodeText,
                sa.ForeignKey("package.id", ondelete="CASCADE", onupdate="CASCADE"),
                primary_key=True,
                nullable=False,
            ),
            sa.Column("feedback", sa.UnicodeText, nullable=True),
            sa.Column(
                "status",
                sa.Enum(
                    ApprovalStatus, 
                    name="status_enum"
                    ), 
                nullable=False, 
                default=ApprovalStatus.PENDING
            )
        )


def downgrade():
    op.drop_table("showcase_package_association")
    op.drop_table("showcase_admin")
    op.drop_table("showcase_approval")
