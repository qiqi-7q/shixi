from app.core.database import Base
from sqlalchemy import Column, DECIMAL, Date, DateTime, Integer, String, Text
from sqlalchemy.sql import func


class MonitorInfo(Base):
    __tablename__ = "monitor_infos"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    test_date = Column(Date, index=True, comment="日期")
    vin_code = Column(String(17), index=True, comment="测试车辆VIN号")
    device_code = Column(String(50), comment="设备号")

    fatigue = Column(Integer, comment="疲劳驾驶次数")
    calling = Column(Integer, comment="接打电话次数")
    smoke = Column(Integer, comment="抽烟次数")
    distract = Column(Integer, comment="分神驾驶次数")
    abnormal = Column(Integer, comment="驾驶员异常次数")
    snapshot = Column(Integer, comment="自动抓拍次数")
    driver_change = Column(Integer, comment="驾驶员变更次数")
    no_belt = Column(Integer, comment="未系安全带次数")

    mileage = Column(DECIMAL(10, 1), comment="行驶里程(km)")
    duration = Column(Integer, comment="车辆上电时长(s)")

    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")


class AlarmRecord(Base):
    """实时报警记录表"""

    __tablename__ = "alarm_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="序号")
    alarm_id = Column(String(64), index=True, comment="平台报警流水号(alarmID)")
    alarm_time = Column(DateTime, nullable=False, comment="报警时间")
    alarm_type = Column(String(100), nullable=False, comment="报警类型")
    speed = Column(DECIMAL(10, 2), nullable=True, comment="速度")
    vin_code = Column(String(50), comment="车辆VIN号")
    remark = Column(Text, comment="备注")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")