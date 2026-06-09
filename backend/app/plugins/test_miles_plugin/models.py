from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class TestMiles(Base):
    __tablename__ = "test_miles"

    id = Column(Integer, primary_key=True, index=True, comment="主键 ID")
    
    project = Column(String(100), nullable=False, index=True, comment="项目")
    test_version = Column(String(50), index=True, comment="测试版本")
    test_time = Column(DateTime, nullable=False, index=True, comment="测试时间")
    vin_code = Column(String(17), index=True, nullable=False, comment="测试车辆 VIN")
    test_function = Column(String(200), index=True, comment="测试功能")
    mileage = Column(Float, comment="里程（取测试里程和实际里程的较小值）")
    is_kpi = Column(Boolean, default=False, comment="是否用于 KPI 统计")
    remarks = Column(Text, comment="备注")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
