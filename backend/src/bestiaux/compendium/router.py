import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from bestiaux.auth.domain import UserEntity
from bestiaux.compendium.schemas import (
    AlleleDetailResponse,
    CreatureDetailResponse,
    CreatureSummaryResponse,
    FormEntryResponse,
    FormsResponse,
    GenomeGeneResponse,
    HistoryResponse,
    UnlockedAllelesResponse,
)
from bestiaux.compendium.service import CompendiumService, CreatureDetail
from bestiaux.core.dependencies import get_current_user, get_db
from bestiaux.core.exceptions import NotFoundError

router = APIRouter(prefix="/compendium", tags=["compendium"])


def _get_service(db: AsyncSession = Depends(get_db)) -> CompendiumService:
    return CompendiumService(session=db)


@router.get("/forms", response_model=FormsResponse)
async def get_forms(
    user: UserEntity = Depends(get_current_user),
    service: CompendiumService = Depends(_get_service),
) -> FormsResponse:
    entries = await service.get_forms(user.id)
    return FormsResponse(
        forms=[
            FormEntryResponse(
                form_id=e.form_id,
                biome_id=e.biome_id,
                level=e.level,
                dominant_stats=e.dominant_stats,
                discovered=e.discovered,
                latest_creature_id=e.latest_creature_id,
                latest_creature_name=e.latest_creature_name,
            )
            for e in entries
        ]
    )


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    user: UserEntity = Depends(get_current_user),
    service: CompendiumService = Depends(_get_service),
) -> HistoryResponse:
    creatures = await service.get_history(user.id)
    return HistoryResponse(
        creatures=[
            CreatureSummaryResponse(
                id=c.id,
                name=c.name,
                generation=c.generation,
                life_stage=c.life_stage,
                is_alive=c.is_alive,
                is_active=c.is_active,
                biome_id=c.biome_id,
                form_id=c.form_id,
                training_force=c.training_force,
                training_beauty=c.training_beauty,
                training_size=c.training_size,
                max_stage_reached=c.max_stage_reached,
                created_at=c.created_at,
            )
            for c in creatures
        ]
    )


@router.get("/creature/{creature_id}", response_model=CreatureDetailResponse)
async def get_creature_detail(
    creature_id: uuid.UUID,
    user: UserEntity = Depends(get_current_user),
    service: CompendiumService = Depends(_get_service),
) -> CreatureDetailResponse:
    detail = await service.get_creature_detail(user.id, creature_id)
    if detail is None:
        raise NotFoundError("Creature not found")
    return _to_detail_response(detail)


@router.get("/alleles", response_model=UnlockedAllelesResponse)
async def get_unlocked_alleles(
    user: UserEntity = Depends(get_current_user),
    service: CompendiumService = Depends(_get_service),
) -> UnlockedAllelesResponse:
    alleles = await service.get_unlocked_alleles(user.id)
    return UnlockedAllelesResponse(
        alleles=[
            AlleleDetailResponse(
                id=a.id,
                trait_category=a.trait_category,
                name=a.name,
                is_dominant=a.is_dominant,
                sprite_key=a.sprite_key,
            )
            for a in alleles
        ]
    )


def _to_detail_response(detail: CreatureDetail) -> CreatureDetailResponse:
    return CreatureDetailResponse(
        id=detail.id,
        name=detail.name,
        generation=detail.generation,
        life_stage=detail.life_stage,
        is_alive=detail.is_alive,
        biome_id=detail.biome_id,
        form_id=detail.form_id,
        training_force=detail.training_force,
        training_beauty=detail.training_beauty,
        training_size=detail.training_size,
        autonomy=detail.autonomy,
        hunger=detail.hunger,
        health=detail.health,
        happiness=detail.happiness,
        genome=[
            GenomeGeneResponse(
                trait_category=g.trait_category,
                allele_from_parent1=g.allele_from_parent1,
                allele_from_parent2=g.allele_from_parent2,
                expressed_allele=g.expressed_allele,
            )
            for g in detail.genome
        ],
        parent1_id=detail.parent1_id,
        parent2_id=detail.parent2_id,
        created_at=detail.created_at,
    )
