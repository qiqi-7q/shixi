from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class VehicleStatus(str, enum.Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"
    MAINTENANCE = "maintenance"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_code = Column(String(50), unique=True, index=True, nullable=False, comment="车辆编号")
    vin = Column(String(17), unique=True, index=True, nullable=False, comment="VIN号")
    model = Column(String(100), nullable=False, comment="车型")
    configuration = Column(String(200), comment="车辆配置")
    plate_number = Column(String(20), comment="车牌号")
    temp_plate_expire_date = Column(Date, comment="临牌到期时间")
    owner_name = Column(String(100), comment="车主姓名")
    parking_location = Column(String(200), comment="停放位置")
    temp_plate_count = Column(Integer, default=0, comment="临牌已办理次数")
    status = Column(Enum(VehicleStatus), default=VehicleStatus.AVAILABLE, comment="车辆状态")
    remarks = Column(Text, comment="备注")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="信息更新时间")

    # 关联借用记录
    borrow_records = relationship("BorrowRecord", back_populates="vehicle")


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    vehicle_code = Column(String(50), comment="车辆编号")
    model = Column(String(100), comment="车型")
    vin = Column(String(17), comment="VIN号")
    borrow_time = Column(DateTime, nullable=False, comment="借用时间")
    return_time = Column(DateTime, comment="归还时间")
    borrower = Column(String(100), nullable=False, comment="借用人")
    driver_name = Column(String(100), comment="司机姓名")
    task_content = Column(Text, comment="任务内容")
    status = Column(String(20), default="active", comment="借用状态: active/returned/cancelled")
    remarks = Column(Text, comment="备注")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关联车辆
    vehicle = relationship("Vehicle", back_populates="borrow_records")