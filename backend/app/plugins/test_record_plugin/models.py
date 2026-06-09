import enum

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


# # 问题分类枚举（可扩展）
# class ProblemCategory(str, enum.Enum):
#     FUNCTION = "function"  # 功能问题
#     PERFORMANCE = "performance"  # 性能问题
#     INTERFACE = "interface"  # 界面问题
#     SYSTEM = "system"  # 系统问题
#     OTHER = "other"  # 其他
#
#
# # 问题现象枚举
# class ProblemPhenomenon(str, enum.Enum):
#     CRASH = "crash"  # 崩溃
#     ABNORMAL = "abnormal"  # 异常
#     DELAY = "delay"  # 延迟
#     DISPLAY_ERROR = "display_error"  # 显示错误
#     OTHER = "other"
#
#
# # 接管类型枚举
# class TakeoverType(str, enum.Enum):
#     MANUAL = "manual"  # 人工接管
#     AUTOMATIC = "automatic"  # 自动接管
#     NO_TAKEOVER = "no_takeover"  # 未接管


class FunctionMode(str, enum.Enum):
    NAP = "NAP"  # NAP模式
    CNAP = "CNAP"  # CNAP模式
    ACC_LCC = "ACC/LCC"  # ACC/LCC模式


# 测试记录表（核心）
class TestRecord(Base):
    __tablename__ = "test_records"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")

    # 你要求的固定字段
    project = Column(String(100), nullable=False, comment="项目")
    car_type = Column(String(100), nullable=False, comment="车型")
    function_mode = Column(
        Enum(FunctionMode), index=True, default=FunctionMode.NAP, comment="功能模式"
    )
    problem_desc = Column(Text, comment="问题描述")
    problem_category = Column(
        String(100), comment="评价维度"
    )  # 可靠性、法规安全、舒适性、可用性、其他 -->问题大类打分使用
    kpi_type = Column(String(100), comment="KPI项")  # 新增KPI项，打分使用
    problem_scene = Column(String(100), comment="问题场景")  # 对应一级
    problem_type = Column(String(100), comment="问题分类")
    problem_phenomenon = Column(String(100), comment="问题现象")  # 对应四级
    takeover_type = Column(String(100), comment="接管类型")
    problem_time = Column(DateTime, nullable=False, comment="问题时间")
    vin_code = Column(String(50), index=True, nullable=False, comment="车辆VIN号")
    data_link = Column(String(500), comment="数据链接")
    wetrack_link = Column(String(500), comment="Wetrack链接")
    analyze_result = Column(Text, comment="分析结果")
    analyze_user = Column(String(50), comment="分析人员")
    analyze_attach = Column(String(500), comment="分析附件")
    software_version = Column(String(50), comment="软件版本")
    remarks = Column(Text, comment="备注")

    # # 自定义扩展字段（JSON格式，支持任意添加字段）
    # custom_fields = Column(JSON, default=dict, comment="自定义扩展字段")

    # 系统字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
