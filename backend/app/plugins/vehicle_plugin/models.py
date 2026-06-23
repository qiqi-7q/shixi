import enum

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


# 数据库存储的以及前端传递的都是英文，返回给前端的是中文
class VehicleStatus(str, enum.Enum):
    AVAILABLE = "可借用"
    BORROWED = "已借出"
    MAINTENANCE = "维护中"


class VehicleGroup(str, enum.Enum):
    DRIVEING = "行车组"
    PARKING = "泊车组"
    WARNNING = "预警组"


class TestStatus(str, enum.Enum):
    ALL_SUPPORT = "支持全部测试"
    NO_PARKING = "不支持泊车测试"
    NO_DRIVING = "不支持行车测试"
    NO_BACKWARNING = "不支持后向预警测试"
    NO_SUPPORT = "不支持全部测试"
    PRODUCING = "生产中"
    BORROWING = "外借中"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    model = Column(String(100), nullable=False, comment="车型")
    group = Column(Enum(VehicleGroup), default=VehicleGroup.DRIVEING, comment="组别")
    vehicle_stage = Column(String(20), comment="车辆阶段")
    configuration = Column(String(200), comment="车辆配置")
    owner_name = Column(String(100), nullable=False, comment="车主权限")
    vehicle_code = Column(
        String(50), unique=True, index=True, nullable=False, comment="车辆编号"
    )
    parking_location = Column(String(200), comment="停车地点")
    vehicle_status = Column(
        Enum(VehicleStatus), default=VehicleStatus.AVAILABLE, comment="使用状态"
    )
    test_status = Column(
        Enum(TestStatus), default=TestStatus.ALL_SUPPORT, comment="车辆状态"
    )
    remarks = Column(Text, comment="备注")
    vin_code = Column(
        String(17), unique=True, index=True, nullable=False, comment="VIN码"
    )

    engine_num = Column(String(100), comment="驱动电机号/发动机号")
    plate_number = Column(String(20), nullable=False, comment="车牌号")
    temp_plate_expire_date = Column(Date, comment="临牌到期时间")
    temp_plate_count = Column(Integer, default=0, comment="临牌已办理次数")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="最后编辑时间"
    )

    # 关联借用记录
    borrow_records = relationship("BorrowRecord", back_populates="vehicle")


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True, index=True)
    model = Column(String(100), comment="车型")
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    vehicle_code = Column(String(50), comment="车辆编号")
    vin_code = Column(String(17), index=True, nullable=False, comment="VIN码")
    borrower = Column(String(100), nullable=False, comment="借用人")
    borrow_time = Column(Date, nullable=False, comment="借用时间")
    driver_name = Column(String(100), comment="司机姓名")
    driver_work = Column(String(50), comment="司机工作安排")
    driver_performance = Column(String(100), comment="司机绩效（有效工时+有效里程）")
    record_creator = Column(String(50), comment="记录创建人")
    created_at = Column(Date, server_default=func.now(), comment="创建时间")
    borrow_status = Column(String(20), default="active", comment="借用状态")
    updated_at = Column(
        Date, server_default=func.now(), onupdate=func.now(), comment="最后编辑时间"
    )
    remarks = Column(Text, comment="备注")
    # 关联车辆
    vehicle = relationship("Vehicle", back_populates="borrow_records")


# 车辆使用率
# class UsageRate(Base):
#     __tablename__ = "usage_rates"
#
#     id = Column(Integer, primary_key=True, index=True)
#     vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
#     vin_code = Column(String(17), index=True, nullable=False, comment="VIN码")
#     fireStatus = Column(Boolean, default=False, comment="使用状态")
#     doorState = Column(Boolean, default=False, comment="门状态")
#     gpsLocation = Column(String(100), comment="GPS位置信息")
#     batteryPower = Column(Integer, comment="电池电量")
#     created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
#     updated_at = Column(
#         DateTime, server_default=func.now(), onupdate=func.now(), comment="最后编辑时间"
#     )
