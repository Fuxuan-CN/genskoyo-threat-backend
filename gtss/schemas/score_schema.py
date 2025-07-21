from pydantic import BaseModel, Field

class GtssScore(BaseModel):
    """GTSS 核心维度评分（0-10分）"""
    active_aggression: float = Field(
        ..., 
        ge=0, 
        le=10,
        description="主动攻击性：10分表示无差别攻击（如芙兰朵露），0分表示完全被动"
    )
    attack_range: float = Field(
        ..., 
        ge=0, 
        le=10,
        description="攻击范围：10分表示全幻想乡（如四季映姬），0分表示仅限单体接触"
    )
    unpredictability: float = Field(
        ..., 
        ge=0, 
        le=10,
        description="不可控性：10分表示完全随机暴走（如芙兰朵露），0分表示完全可控"
    )
    special_ability: float = Field(
        ..., 
        ge=0, 
        le=10,
        description="特殊能力：10分表示规则级能力（如八云紫的境界操纵），0分表示无能力"
    )
    historical_threat: float = Field(
        ..., 
        ge=0, 
        le=10,
        description="历史威胁记录：10分表示多次引发异变（如八云紫），0分表示无记录"
    )
    encounter_probability: float = Field(
        ..., 
        ge=0, 
        le=10,
        description="遭遇概率：10分表示每日必遇，0分表示不会遇到"
    )
