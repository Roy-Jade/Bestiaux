"""seed allele catalog

Revision ID: d7278486924a
Revises: 0c3c01712ce0
Create Date: 2026-06-30 09:34:44.986529

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd7278486924a'
down_revision: Union[str, Sequence[str], None] = '0c3c01712ce0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TRAIT_CATEGORY_ENUM = sa.Enum(
    "EYES", "SKULL_TOP", "DORSAL", "CAUDAL", "COLOR",
    name="traitcategory",
    create_type=False,
)

ALLELE_TABLE = sa.table(
    "alleles",
    sa.column("id", sa.String),
    sa.column("trait_category", TRAIT_CATEGORY_ENUM),
    sa.column("name", sa.String),
    sa.column("is_dominant", sa.Boolean),
    sa.column("sprite_key", sa.String),
    sa.column("biome_id", sa.String),
)

ALLELES = [
    # EYES
    {"id": "round_eyes", "trait_category": "EYES", "name": "Round eyes", "is_dominant": False, "sprite_key": "eyes/round_eyes"},
    {"id": "heart_eyes", "trait_category": "EYES", "name": "Heart eyes", "is_dominant": False, "sprite_key": "eyes/heart_eyes"},
    {"id": "almond_eyes", "trait_category": "EYES", "name": "Almond eyes", "is_dominant": True, "sprite_key": "eyes/almond_eyes"},
    {"id": "big_eyes", "trait_category": "EYES", "name": "Big eyes", "is_dominant": True, "sprite_key": "eyes/big_eyes"},
    # SKULL_TOP
    {"id": "no_horn", "trait_category": "SKULL_TOP", "name": "No horn", "is_dominant": False, "sprite_key": "skull_top/no_horn"},
    {"id": "heart_horn", "trait_category": "SKULL_TOP", "name": "Heart horn", "is_dominant": False, "sprite_key": "skull_top/heart_horn"},
    {"id": "small_horn", "trait_category": "SKULL_TOP", "name": "Small horn", "is_dominant": True, "sprite_key": "skull_top/small_horn"},
    {"id": "small_crest", "trait_category": "SKULL_TOP", "name": "Small crest", "is_dominant": True, "sprite_key": "skull_top/small_crest"},
    # DORSAL
    {"id": "no_dorsal", "trait_category": "DORSAL", "name": "No dorsal", "is_dominant": False, "sprite_key": "dorsal/no_dorsal"},
    {"id": "heart_dorsal", "trait_category": "DORSAL", "name": "Heart dorsal", "is_dominant": False, "sprite_key": "dorsal/heart_dorsal"},
    {"id": "small_wings", "trait_category": "DORSAL", "name": "Small wings", "is_dominant": True, "sprite_key": "dorsal/small_wings"},
    {"id": "small_spikes", "trait_category": "DORSAL", "name": "Small spikes", "is_dominant": True, "sprite_key": "dorsal/small_spikes"},
    # CAUDAL
    {"id": "no_tail", "trait_category": "CAUDAL", "name": "No tail", "is_dominant": False, "sprite_key": "caudal/no_tail"},
    {"id": "heart_tail", "trait_category": "CAUDAL", "name": "Heart tail", "is_dominant": False, "sprite_key": "caudal/heart_tail"},
    {"id": "short_tail", "trait_category": "CAUDAL", "name": "Short tail", "is_dominant": True, "sprite_key": "caudal/short_tail"},
    {"id": "short_fin_tail", "trait_category": "CAUDAL", "name": "Short fin tail", "is_dominant": True, "sprite_key": "caudal/short_fin_tail"},
    # COLOR
    {"id": "light_grey", "trait_category": "COLOR", "name": "Light grey", "is_dominant": False, "sprite_key": "color/light_grey"},
    {"id": "pink", "trait_category": "COLOR", "name": "Pink", "is_dominant": False, "sprite_key": "color/pink"},
    {"id": "light_blue", "trait_category": "COLOR", "name": "Light blue", "is_dominant": True, "sprite_key": "color/light_blue"},
    {"id": "light_green", "trait_category": "COLOR", "name": "Light green", "is_dominant": True, "sprite_key": "color/light_green"},
    {"id": "light_red", "trait_category": "COLOR", "name": "Light red", "is_dominant": True, "sprite_key": "color/light_red"},
]


def upgrade() -> None:
    op.bulk_insert(ALLELE_TABLE, ALLELES)


def downgrade() -> None:
    allele_ids = [allele["id"] for allele in ALLELES]
    op.execute(
        ALLELE_TABLE.delete().where(ALLELE_TABLE.c.id.in_(allele_ids))
    )
