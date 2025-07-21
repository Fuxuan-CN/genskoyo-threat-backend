
from .score_schema import GtssScore
from pydantic import BaseModel, Field

class CharacterCard(BaseModel):
    """角色完整数据模型（含GTSS评分）"""

    name: str = Field(..., description="角色名称（如“博丽灵梦”）")
    race: str = Field(..., description="种族（如“人类”“妖怪”）")
    affiliation: str = Field(..., description="所属势力（如“博丽神社”“红魔馆”）")
    gtss: GtssScore = Field(..., description="GTSS威胁评分")
    survival_tip: str = Field(..., description="生存建议（如“保持礼貌距离”）")
    image_url: str = Field(..., description="角色图片URL")

class PageMeta(BaseModel):
    """ 此页元数据 """
    page: int
    """ 页数 """
    page_size: int
    """ 页面大小 """
    total: int
    """ 总共数据 """
    total_pages: int
    """ 总共页数 """

class CharacterPageResponse(BaseModel):
    """ 分页响应 """
    data: list[CharacterCard]
    """ 所有数据 """
    page_meta: PageMeta
    """ 页面元数据 """