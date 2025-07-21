
from datetime import datetime
from typing import Sequence, Any
from sqlalchemy.orm import joinedload
from sqlalchemy import select , func
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas.database_schema import CharacterDB, GtssScoreDB
from .schemas.data_schema import CharacterCard
from .logger import logger


class CharacterCRUD:
    """ GTSS评分（增删改查）"""
    @staticmethod
    async def create(db: AsyncSession, character: CharacterCard) -> CharacterDB:
        """新增角色（连带GTSS评分）"""
        try:
            # 创建角色主表记录
            logger.info(f"创建角色: {character.name}")
            db_character = CharacterDB(
                name=character.name,
                race=character.race,
                affiliation=character.affiliation,
                survival_tip=character.survival_tip,
                image_url=character.image_url,
                last_update=datetime.now()
            )
            db.add(db_character)
            await db.commit()
            await db.refresh(db_character)

            # 创建关联的GTSS评分记录
            db_gtss = GtssScoreDB(
                character_id=db_character.id,
                **character.gtss.model_dump(),
                last_update=datetime.now()
            )
            db.add(db_gtss)
            await db.commit()
            return db_character
        except Exception as e:
            logger.error(f"创建角色失败: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> CharacterDB | None:
        """查询角色（连带GTSS评分）"""
        try:
            logger.info(f"查询角色: {name}")
            result = await db.execute(
                select(CharacterDB)
                .options(joinedload(CharacterDB.gtss_score))
                .where(CharacterDB.name == name)
            )
            return result.scalars().first()
        except Exception as e:
            logger.error(f"查询角色失败: {e}")
            raise

    @staticmethod
    async def get_all(db: AsyncSession) -> Sequence[CharacterDB]:
        """ 获取所有角色 """
        try:
            logger.info("获取所有角色...")
            result = await db.execute(
                select(CharacterDB).options(joinedload(CharacterDB.gtss_score))
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"获取所有角色出错: {e}")
            raise

    @staticmethod
    async def get_paginated_characters(
        db: AsyncSession, 
        page: int = 1, 
        page_size: int = 10
    ) -> tuple[Sequence[CharacterDB], int]:
        """分页查询角色列表，返回 (当前页数据, 总条数)"""
        try:
            # 查询总条数
            total = (await db.execute(select(func.count(CharacterDB.id)))).scalar()
            
            # 分页查询数据
            result = await db.execute(
                select(CharacterDB)
                .options(joinedload(CharacterDB.gtss_score))
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            characters = result.scalars().all()
            return characters, total or 0
        except Exception as e:
            logger.error(f"分页查询失败: {e}")
            raise

    @staticmethod
    def _update_if_changed(target_obj: Any, source_data: Any, fields: list[str], prefix: str = "") -> bool:
        """
        比较并更新目标对象中发生变化的字段
        :param target_obj: 要更新的目标对象
        :param source_data: 包含新数据的对象
        :param fields: 要检查的字段列表
        :param prefix: 日志前缀(可选)
        :return: 是否有字段被更新
        """
        updated = False
        source_dict = source_data.model_dump(exclude_unset=True) if hasattr(source_data, "model_dump") else source_data
        
        for field in fields:
            if field in source_dict:
                new_value = getattr(source_data, field)
                old_value = getattr(target_obj, field)
                if new_value != old_value:
                    logger.debug(f"{prefix}更新字段: {field} (旧值: {old_value}, 新值: {new_value})")
                    setattr(target_obj, field, new_value)
                    updated = True
        
        return updated

    @staticmethod
    async def update(db: AsyncSession, name: str, new_data: CharacterCard) -> CharacterDB | None:
        """更新角色数据（连带GTSS评分），仅更新实际发生变化的字段"""
        try:
            logger.info(f"更新角色: {name}")
            db_character = await CharacterCRUD.get_by_name(db, name)
            if not db_character:
                return None

            # 更新主表字段
            main_fields = ["name", "race", "affiliation", "survival_tip", "image"]
            main_updated = CharacterCRUD._update_if_changed(
                db_character, 
                new_data, 
                main_fields,
                "角色"
            )
            
            # 只有字段实际变化时才更新时间戳
            if main_updated:
                db_character.last_update = datetime.now()  # type: ignore

            # 更新GTSS评分表字段
            gtss_updated = False
            if hasattr(new_data, "gtss") and new_data.gtss:
                gtss_updated = CharacterCRUD._update_if_changed(
                    db_character.gtss_score,
                    new_data.gtss,
                    list(new_data.gtss.model_dump(exclude_unset=True).keys()),
                    "GTSS"
                )
                
                if gtss_updated:
                    db_character.gtss_score.last_update = datetime.now()

            # 只有实际有更新时才提交
            if main_updated or gtss_updated:
                await db.commit()
                await db.refresh(db_character)
            
            return db_character
        except Exception as e:
            logger.error(f"更新角色失败: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def delete(db: AsyncSession, name: str) -> bool:
        """删除角色"""
        try:
            logger.info(f"删除角色: {name}")
            db_character = await CharacterCRUD.get_by_name(db, name)
            if not db_character:
                return False
            await db.delete(db_character)
            await db.commit()
            return True
        except Exception as e:
            logger.error(f"删除角色失败: {e}")
            await db.rollback()
            raise
    
    @staticmethod
    async def get_by_threat_level(db: AsyncSession, level: str) -> list[CharacterDB]:
        """根据威胁等级筛选角色"""
        try:
            result = await db.execute(
                select(CharacterDB)
                .options(joinedload(CharacterDB.gtss_score))
            )
            all_chars = result.scalars().all()
            return [c for c in all_chars if _calculate_threat_level(c) == level]
        except Exception as e:
            logger.error(f"按威胁等级查询失败: {e}")
            raise

def _calculate_threat_level(character: CharacterDB) -> str:
    """内部方法：计算威胁等级（S/A/B/C/D）"""
    gtss: GtssScoreDB = character.gtss_score  # 通过关系属性访问分表数据
    base_score: float = (
        gtss.active_aggression     * 0.25 +
        gtss.attack_range          * 0.20 +
        gtss.unpredictability      * 0.20 +
        gtss.special_ability       * 0.15 +
        gtss.historical_threat     * 0.10 +
        gtss.encounter_probability * 0.10
    ) # type: ignore

    final_score: float = base_score

    match final_score:
        case fs if fs >= 9.0: return "S"
        case fs if fs >= 7.0: return "A"
        case fs if fs >= 5.0: return "B"
        case fs if fs >= 2.0: return "C"
        case _:               return "D"
