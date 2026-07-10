from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Enum, Boolean
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime
from typing import Optional

# 定义任务状态枚举
class TaskStatus(str):
    """任务状态枚举"""
    COMPLETED = "完成"
    IN_PROGRESS = "进行中"
    NOT_STARTED = "未开始"
    NOT_ACHIEVED = "未达标"
    SUSPENDED = "挂起"
    
    # 获取所有可选值
    @classmethod
    def values(cls):
        return [cls.COMPLETED, cls.IN_PROGRESS, cls.NOT_STARTED, cls.NOT_ACHIEVED, cls.SUSPENDED]

class TestTask(Base):
    __tablename__ = "test_tasks"

    id = Column(Integer, primary_key=True, index=True, comment="主键 ID")
    
    project = Column(String(100), nullable=False, index=True, comment="项目")
    test_version = Column(String(50), comment="测试版本")
    test_time = Column(DateTime, nullable=False, index=True, comment="测试时间")
    vin_code = Column(String(17), index=True, nullable=False, comment="测试车辆 VIN")
    test_function = Column(String(200), index=True, comment="测试功能")
    task_desc = Column(Text, comment="任务描述")
    task_publisher = Column(String(50), index=True, comment="任务发布人")
    test_mileage = Column(Float, comment="测试里程")
    test_person = Column(String(100), index=True, comment="测试人员")
    actual_mileage = Column(Float, comment="实际完成里程")
    task_achievement_rate = Column(Float, comment="任务达成率")
    
    task_status = Column(Enum(*TaskStatus.values(), name='task_status_enum', native_enum=False, length=64), 
                        index=True, 
                        default=TaskStatus.NOT_STARTED, 
                        comment="任务状态")
    is_kpi = Column(Boolean, default=False, comment="是否用于 KPI 统计")
    reason_desc = Column(Text, comment="原因说明")
    
    remarks = Column(Text, comment="备注")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")