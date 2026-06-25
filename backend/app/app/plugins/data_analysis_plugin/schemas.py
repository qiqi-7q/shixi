from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ========== KpiMain Schemas ==========
class KpiMainBase(BaseModel):
    """KPI总表基础模型 - 创建和更新时的核心字段"""

    project: str = Field(..., max_length=50, description="项目")
    carModel: str = Field(..., max_length=50, description="车型")
    version: str = Field(..., max_length=50, description="版本")
    funcMode: str = Field(..., max_length=50, description="功能模式")
    kpiMileage: Decimal = Field(..., description="KPI里程")
    totalScore: Decimal = Field(..., description="总分")


# 创建
class KpiMainCreate(KpiMainBase):
    """创建KPI总表请求模型"""

    pass


# 更新
class KpiMainUpdate(BaseModel):
    """更新KPI总表请求模型 - 所有字段可选"""

    project: str = Field(..., max_length=50, description="项目")
    carModel: str = Field(..., max_length=50, description="车型")
    version: str = Field(..., max_length=50, description="版本")
    funcMode: str = Field(..., max_length=50, description="功能模式")
    kpiMileage: Decimal = Field(..., description="KPI里程")
    totalScore: Decimal = Field(..., description="总分")


# 响应模型
class KpiMainResponse(KpiMainBase):
    """KPI总表响应模型 - 包含数据库自动生成的字段"""

    id: int
    create_time: datetime
    update_time: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== KpiModule Schemas ==========
class KpiModuleBase(BaseModel):
    """KPI模块表基础模型 - 创建和更新时的核心字段"""

    main_id: int = Field(..., description="关联总表ID")
    reliability: Decimal = Field(..., description="可靠性")
    regulationsSafety: Decimal = Field(..., description="法规\安全性")
    comfort: Decimal = Field(..., description="舒适性")
    usability: Decimal = Field(..., description="可用性")


# 创建
class KpiModuleCreate(KpiModuleBase):
    """创建KPI模块表请求模型"""

    pass


# 更新
class KpiModuleUpdate(BaseModel):
    """更新KPI模块表请求模型 - 所有字段可选"""

    main_id: int = Field(..., description="关联总表ID")
    reliability: Decimal = Field(..., description="可靠性")
    regulationsSafety: Decimal = Field(..., description="法规\安全性")
    comfort: Decimal = Field(..., description="舒适性")
    usability: Decimal = Field(..., description="可用性")


# 响应模型
class KpiModuleResponse(KpiModuleBase):
    """KPI模块表响应模型 - 包含数据库自动生成的字段"""

    id: int
    create_time: datetime
    update_time: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== KpiItem Schemas ==========
class KpiItemBase(BaseModel):
    """KPI明细项表基础模型 - 创建和更新时的核心字段"""

    module_id: int = Field(..., description="关联模块表ID")
    KPIType: str = Field(..., description="KPI项")
    KPICount: int = Field(..., description="KPI项数量")
    MPI: int = Field(..., description="舒适性")
    KPIScore: Decimal = Field(..., description="KPI项加权得分")


# 创建
class KpiItemCreate(KpiItemBase):
    """创建KPI明细项表请求模型"""

    pass


# 更新
class KpiItemUpdate(BaseModel):
    """更新KPI明细项表请求模型 - 所有字段可选"""

    module_id: int = Field(..., description="关联模块表ID")
    KPIType: str = Field(..., description="KPI项")
    KPICount: int = Field(..., description="KPI项数量")
    MPI: int = Field(..., description="舒适性")
    KPIScore: Decimal = Field(..., description="KPI项加权得分")


# 响应模型
class KpiItemResponse(KpiItemBase):
    """KPI明细项表响应模型 - 包含数据库自动生成的字段"""

    id: int
    create_time: datetime
    update_time: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== 手动更新成功率请求模型 ==========
class UpdateSuccessRateRequest(BaseModel):
    """手动更新成功率指标请求模型"""
    
    project: str = Field(..., description="项目")
    carModel: str = Field(..., description="车型")
    version: str = Field(..., description="版本")
    funcMode: str = Field(..., description="功能模式")
    
    # 成功率指标（0-100，表示百分比）
    change_lane_success_rate: float = Field(..., ge=0, le=100, description="变道成功率(%)")
    inflow_success_rate: float = Field(..., ge=0, le=100, description="汇入成功率(%)")
    outflow_success_rate: float = Field(..., ge=0, le=100, description="汇出成功率(%)")
    diverge_converge_rate: float = Field(..., ge=0, le=100, description="分合流成功率(%)")
    special_rate: float = Field(..., ge=0, le=100, description="特殊场景成功率(%)")
    recog_rate: float = Field(..., ge=0, le=100, description="限速识别成功率(%)")
