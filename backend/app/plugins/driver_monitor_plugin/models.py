import enum
from app.core.database import Base
from sqlalchemy import Column, DECIMAL, Date, DateTime, Enum, Integer, String, Text
from sqlalchemy.sql import func



class DriverStatus(enum.Enum):
    NORMAL = "正常"
    FATIGUE = "疲劳"
    MILDFAIR = "轻微疲劳"
    SEVEREFATIGUE = "严重疲劳"


class DriverMonitor(Base):
    __tablename__ = "driver_monitors"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    test_date = Column(Date, nullable=False, comment="日期")

    test_start_time = Column(DateTime, nullable=False, comment="测试开始时间")
    test_end_time = Column(DateTime, nullable=False, comment="测试结束时间")
    driver_status = Column(
        Enum(DriverStatus, native_enum=False, length=64),
        default=DriverStatus.NORMAL,
        nullable=False,
        comment="司机状态",
    )
    vin_code = Column(
        String(17), unique=True, index=True, nullable=False, comment="测试车辆VIN号"
    )
    driver_name = Column(String(50), nullable=False, comment="司机姓名")
    dms_trigger_count = Column(Integer, nullable=False, comment="DMS触发次数")

    distance = Column(DECIMAL(10, 2), nullable=False, comment="行驶里程")

    power_start_duration = Column(DateTime, nullable=False, comment="车辆上电开始时间")
    power_end_duration = Column(DateTime, nullable=False, comment="车辆上电结束时间")

    remark = Column(Text, comment="备注")

    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
