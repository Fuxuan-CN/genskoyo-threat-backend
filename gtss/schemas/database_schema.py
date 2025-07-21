from sqlalchemy import Column, String, Float, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from .score_schema import GtssScore
from .data_schema import CharacterCard
from datetime import datetime

Base = declarative_base()

class GtssScoreDB(Base):
    """GTSS评分分表模型"""
    __tablename__ = "gtss_scores"

    id                    = Column(Integer, primary_key=True, autoincrement=True)

    character_id          = Column(Integer, ForeignKey("characters.id"), index=True, unique=True, nullable=False)
    
    active_aggression     = Column(Float)
    attack_range          = Column(Float)
    unpredictability      = Column(Float)
    special_ability       = Column(Float)
    historical_threat     = Column(Float)
    encounter_probability = Column(Float)

    character             = relationship("CharacterDB", back_populates="gtss_score")

    last_update           = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

class CharacterDB(Base):
    """角色主表模型"""
    __tablename__ = "characters"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    name          = Column(String(50), unique=True, nullable=False)
    race          = Column(String(20))
    affiliation   = Column(String(50))
    survival_tip  = Column(Text)
    image_url     = Column(String())
    gtss_score    = relationship("GtssScoreDB", back_populates="character", uselist=False)
    last_update   = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    def to_pydantic(self) -> CharacterCard:
        """将数据库对象转为Pydantic模型"""
        return CharacterCard(
            name=self.name, # type: ignore
            race=self.race, # type: ignore
            affiliation=self.affiliation, # type: ignore
            gtss=GtssScore(
                active_aggression=self.gtss_score.active_aggression,
                attack_range=self.gtss_score.attack_range,
                unpredictability=self.gtss_score.unpredictability,
                special_ability=self.gtss_score.special_ability,
                historical_threat=self.gtss_score.historical_threat,
                encounter_probability=self.gtss_score.encounter_probability,
            ),
            survival_tip=self.survival_tip, # type: ignore
            image_url=self.image_url # type: ignore
        )