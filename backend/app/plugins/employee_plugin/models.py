from sqlalchemy import Column, DATE, Integer, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum


# 岗位类型枚举
class JobType(str, Enum):
    DRIVER = "司机"  # 司机
    OUTSOURCE = "外协工程师"  # 外协
    OFFICIAL = "正式员工"  # 正式员工


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    # 新增字段
    card_validity = Column(DATE, comment="内照有效期")
    module_name = Column(String(100), index=True, comment="模块名称")
    module_manager = Column(String(100), comment="模块负责人")
    name = Column(String(100), nullable=False, index=True, comment="姓名")
    job_type = Column(
        SQLEnum(JobType, values_callable=lambda obj: [e.value for e in obj],native_enum=False,length=64),
        comment="岗位（司机/外协）",
 )
    task = Column(String(100), comment="负责任务")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )