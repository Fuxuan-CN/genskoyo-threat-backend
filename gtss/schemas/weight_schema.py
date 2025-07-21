
from pydantic import BaseModel

class GTSSWeights(BaseModel):
    """ GTSS评分权重 """
    active_aggression: float     = 0.25
    """ 主动攻击性 """
    attack_range: float          = 0.20
    """ 攻击范围 """
    unpredictability: float      = 0.20
    """ 不可控性 """
    special_ability: float       = 0.15
    """ 特殊能力 """
    historical_threat: float     = 0.10
    """ 历史威胁 """
    encounter_probability: float = 0.10
    """ 概率接触 """