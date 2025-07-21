from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db_session 
from .crud import CharacterCRUD
from .schemas.data_schema import CharacterCard, CharacterPageResponse, PageMeta
from .schemas.weight_schema import GTSSWeights

GTSS = APIRouter(prefix="/gtdb", tags=["GTDB API"])

@GTSS.get("/weight")
async def get_weight() -> GTSSWeights:
    """ 返回评分权重 """
    return GTSSWeights()

@GTSS.post("/characters")
async def create_character(
    character: CharacterCard, 
    db: AsyncSession = Depends(get_db_session)
) -> dict[str, str]:
    """新增角色到数据库"""
    if await CharacterCRUD.get_by_name(db, character.name):
        raise HTTPException(status_code=400, detail="角色已存在")
    db_character = await CharacterCRUD.create(db, character)
    return {"message": "角色添加成功"}

@GTSS.get("/characters")
async def get_all_characters(
    db: AsyncSession = Depends(get_db_session),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数")
) -> CharacterPageResponse:
    """获取分页角色列表"""
    characters, total = await CharacterCRUD.get_paginated_characters(db, page, page_size)
    _data = [c.to_pydantic() for c in characters]
    _total_pages = (total + page_size - 1) // page_size
    _page_meta = PageMeta(page=page, page_size=page_size, total=total, total_pages=_total_pages)
    _resp = CharacterPageResponse(data=_data, page_meta=_page_meta)
    return _resp

@GTSS.get("/characters/{name}")
async def get_character(name: str, db: AsyncSession = Depends(get_db_session)) -> CharacterCard:
    """查询角色详情"""
    db_character = await CharacterCRUD.get_by_name(db, name)
    if not db_character:
        raise HTTPException(status_code=404, detail="角色不存在")
    return db_character.to_pydantic()

@GTSS.put("/characters/{name}")
async def update_character(
    name: str, 
    new_data: CharacterCard, 
    db: AsyncSession = Depends(get_db_session)
) -> dict[str, str]:
    """更新角色数据"""
    db_character = await CharacterCRUD.update(db, name, new_data)
    if not db_character:
        raise HTTPException(status_code=404, detail="角色不存在")
    return {"message": "角色更新成功"}

@GTSS.delete("/characters/{name}")
async def delete_character(name: str, db: AsyncSession = Depends(get_db_session)):
    """删除角色"""
    if not await CharacterCRUD.delete(db, name):
        raise HTTPException(status_code=404, detail="角色不存在")
    return {"message": "角色已删除"}

@GTSS.get("/characters/by-level/{level}")
async def get_characters_by_level(level: str, db: AsyncSession = Depends(get_db_session)) -> list[CharacterCard]:
    """根据威胁等级筛选角色"""
    valid_levels = {"S", "A", "B", "C", "D"}
    if level not in valid_levels:
        raise HTTPException(status_code=400, detail="无效的威胁等级")
    characters = await CharacterCRUD.get_by_threat_level(db, level)
    return [c.to_pydantic() for c in characters]