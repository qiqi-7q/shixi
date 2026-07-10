try:
    from cgitb import text
except ImportError:
    # Python 3.13+ 移除了 cgitb，提供兼容层
    def text(info, context=5):
        import traceback

        return "".join(traceback.format_exception(*info))


import enum

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class FunctionMode(str, enum.Enum):
    NAP = "NAP"  # NAP模式
    CNAP = "CNAP"  # CNAP模式
    ACC_LCC = "ACC/LCC"  # ACC/LCC模式


class EvaluationDimension(str, enum.Enum):
    """评价维度枚举"""

    RELIABILITY = "可靠性"  # 可靠性
    REGUSAFETY = "法规/安全性"  # 法规/安全性
    COMFORT = "舒适性"  # 舒适性
    USABILITY = "可用性"  # 可用性


class KPIType(str, enum.Enum):
    """KPI项枚举"""

    EXIT = "异常退出"  # 异常退出
    DOWNGRADE = "异常降级"  # 异常降级
    UNACTIVATE = "无法激活"  # 无法激活
    EXCEPTION = "系统异常"  # 系统异常
    COLLISION = "碰撞风险"  # 碰撞风险
    CRASH = "压实线"  # 压实线
    RED_GREEN_SEVERE = "匝道红绿灯严重失效（导致闯红灯）"  # 匝道红绿灯严重失效
    RED_GREEN_GENERAL = "匝道红绿灯一般失效（错误减速/加速）"  # 匝道红绿灯一般失效
    OVER_LOW = "超速/低速"  # 超速/低速
    LATERAL = "横向"  # 横向
    VERTICAL = "纵向"  # 纵向
    CHANGELANE_S = "变道成功"  # 变道成功
    CHANGELANE_F = "变道失败"  # 变道失败
    UNAVA_CHANGELANE = "无效变道（如无必要的反复变道）"  # 无效变道
    INFLOW_S = "汇入成功"  # 汇入成功
    INFLOW_F = "汇入失败"  # 汇入失败
    OUTFLOW_S = "汇出成功"  # 汇出成功
    OUTFLOW_F = "汇出失败"  # 汇出失败
    DIVERGE_CONVERGE_S = "分合流成功"  # 分合流成功
    DIVERGE_CONVERGE_F = "分合流失败"  # 分合流失败
    SPECIAL_S = "特殊场景通过成功"  # 特殊场景通过成功
    SPECIAL_F = "特殊场景通过失败"  # 特殊场景通过失败
    DROPPED = "脱手监测"  # 脱手监测
    RECOG_S = "限速识别成功"  # 限速识别成功
    RECOG_F = "限速识别失败"  # 限速识别失败
    H_M_C = "人机共驾接管冲突"  # 人机共驾接管冲突
    H_M_U = "人机共驾车辆失控风险"  # 人机共驾车辆失控风险
    MICRO_OA_FAIL = "微避障失败（未避让非机动车/行人/静止障碍物）"  # 微避障失败
    MICRO_OA_B = "微避障急刹/猛打方向"  # 微避障急刹/猛打方向
    MICRO_OA_R = "微避障后无回正、压线"  # 微避障后无回正、压线


# 测试记录表（核心）
class TestRecord(Base):
    __tablename__ = "test_records"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")

    # 你要求的固定字段
    project = Column(String(100), comment="项目")
    car_type = Column(String(100), comment="车型")
    creator = Column(String(50), comment="创建人")
    creator_id = Column(Integer, comment="创建人ID")
    function_mode = Column(
        Enum(FunctionMode, native_enum=False, length=64), index=True, default=FunctionMode.NAP, comment="功能模式"
    )
    problem_desc = Column(Text, comment="问题描述")
    problem_category = Column(
        Enum(EvaluationDimension, native_enum=False, length=64), comment="评价维度"
    )  # 可靠性、法规安全、舒适性、可用性 -->问题大类打分使用
    kpi_type = Column(Enum(KPIType, native_enum=False, length=64), comment="KPI项")  # KPI项，打分使用
    problem_scene = Column(String(100), comment="问题场景")  # 对应一级
    problem_type = Column(String(100), comment="问题分类")
    problem_phenomenon = Column(Text, comment="问题现象")  # 对应四级
    takeover_type = Column(String(100), comment="接管类型")
    problem_time = Column(DateTime, comment="问题时间")
    vin_code = Column(String(17), index=True, comment="车辆VIN号")
    data_link = Column(String(500), comment="数据链接")
    wetrack_link = Column(String(500), comment="Wetrack链接")
    analyze_result = Column(Text, comment="分析结果")
    analyze_user = Column(String(50), comment="分析人员")
    analyze_attach = Column(JSON, default=list, comment="分析附件（多文件路径数组）")
    software_version = Column(String(50), comment="软件版本")
    remarks = Column(Text, comment="备注")

    # # 自定义扩展字段（JSON格式，支持任意添加字段）
    # custom_fields = Column(JSON, default=dict, comment="自定义扩展字段")

    # 系统字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
