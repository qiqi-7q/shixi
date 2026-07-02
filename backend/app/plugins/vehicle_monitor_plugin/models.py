import enum
from app.core.database import Base
from sqlalchemy import Boolean, Column, DECIMAL, Date, DateTime, Integer, String
from sqlalchemy.sql import func


class VehicleMonitor(Base):
    __tablename__ = "vehicle_monitors"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    vin_code = Column(String(17), index=True, nullable=False, comment="车辆VIN号")
    model = Column(String(50), comment="车型")
    group = Column(String(50), comment="组别")
    power = Column(Integer, comment="上电状态(0:未上电, 1:已上电)")
    remoteMQ = Column(Integer, comment="远程MQ状态(0:未连接, 1:已连接)")
    dataMQ = Column(Integer, comment="数采MQ状态(0:未连接, 1:已连接)")
    TCP = Column(Integer, comment="TCP状态(0:未连接, 1:已连接)")
    monitor_date = Column(Date, comment="日期")
    power_duration = Column(DECIMAL(10, 2), comment="上电时长")
    # 百分比存 *100%后的数字
    usage = Column(DECIMAL(10, 2), comment="使用率(%)")
    distance = Column(DECIMAL(10, 2), comment="行驶里程")
    smart_distance = Column(DECIMAL(10, 2), comment="智驾里程")
    position = Column(String(100), comment="位置")
    max_speed = Column(DECIMAL(10, 2), comment="最高车速")
    remain_battery = Column(DECIMAL(10, 2), comment="剩余电量")
    charge_count = Column(Integer, comment="充电次数")
    is_del = Column(Integer, default=0, comment="是否删除(0:未删除, 1:已删除)")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
