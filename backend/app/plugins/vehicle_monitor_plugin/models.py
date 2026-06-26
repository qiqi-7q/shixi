import enum
from app.core.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DECIMAL,
    Date,
    DateTime,
    Enum,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func


class VehicleMonitor(Base):
    __tablename__ = "vehicle_monitors"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    monitor_date = Column(Date, comment="日期")
    vin_code = Column(
        String(17), unique=True, index=True, nullable=False, comment="测试车辆VIN号"
    )
    power_duration = Column(DECIMAL(10, 2), comment="车辆上电时间(小时)")
    usage = Column(DECIMAL(10, 4), comment="使用率")
    distance = Column(DECIMAL(10, 2), comment="里程")
    is_del = Column(Boolean, default=False, comment="是否删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
