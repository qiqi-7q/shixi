from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ========== TestRoute Schemas ==========
class TestRouteBase(BaseModel):
    """测试路线基础模型 - 创建和更新时的核心字段"""
    location: str = Field(..., max_length=100, description="地点")
    route_name: str = Field(..., max_length=100, description="路线名称")
    route_length: Decimal = Field(..., description="路线里程")
    test_func: str = Field(..., max_length=100, description="测试功能")
    diff: Decimal = Field(..., ge=0, le=100, description="难度系数（0-100）")
    creator: str = Field(..., max_length=50, description="创建人")

    # 可选字段
    route_desc: Optional[str] = Field(None, description="路线描述")
    route_feature: Optional[str] = Field(None, max_length=200, description="路线特征")
    route_link: Optional[str] = Field(None, max_length=500, description="路线链接")
    remark: Optional[str] = Field(None, description="备注")


# 创建
class TestRouteCreate(TestRouteBase):
    """创建测试路线请求模型"""

    pass


# 更新
class TestRouteUpdate(BaseModel):
    """更新测试路线请求模型 - 所有字段可选"""
    
    location: Optional[str] = Field(None, max_length=100, description="地点")
    route_name: Optional[str] = Field(None, max_length=100, description="路线名称")
    route_length: Optional[Decimal] = Field(None, description="路线里程")
    test_func: Optional[str] = Field(None, max_length=100, description="测试功能")
    diff: Optional[Decimal] = Field(None, ge=0, le=100, description="难度系数（0-100）")
    route_desc: Optional[str] = Field(None, description="路线描述")
    route_feature: Optional[str] = Field(None, max_length=200, description="路线特征")
    route_link: Optional[str] = Field(None, max_length=500, description="路线链接")
    remark: Optional[str] = Field(None, description="备注")
    creator: Optional[str] = Field(None, max_length=50, description="创建人")


# 批量导入模型
class TestRouteBatchImport(BaseModel):
    """批量导入模型"""

    pass
    # records: List[TestRouteCreate]


# 响应模型
class TestRouteResponse(TestRouteBase):
    """测试路线响应模型 - 包含数据库自动生成的字段"""

    id: int
    create_time: datetime
    update_time: datetime

    model_config = ConfigDict(from_attributes=True)
