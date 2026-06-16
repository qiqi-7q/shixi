from datetime import datetime

from sqlalchemy import Boolean, Column, DECIMAL, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


# 1. 总表：kpi_main
class KpiMain(Base):
    __tablename__ = "kpi_main"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="主键ID")
    project = Column(String(50), nullable=False, index=True, comment="项目")
    carModel = Column(String(50), nullable=False, index=True, comment="车型")
    version = Column(String(50), nullable=False, index=True, comment="版本")
    funcMode = Column(String(50), nullable=False, index=True, comment="功能模式")
    kpiMileage = Column(DECIMAL(10, 2), nullable=False, comment="KPI里程")
    totalScore = Column(DECIMAL(8, 2), nullable=False, comment="总分")
    is_del = Column(Boolean, default=False, comment="是否删除")
    createTime = Column(DateTime, default=datetime.now, comment="创建时间")
    updateTime = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    # 一对多关联：总表 -> 模块表
    module_list = relationship(
        "KpiModule", back_populates="main", cascade="all, delete-orphan"
    )


# 2. 模块表：kpi_module
class KpiModule(Base):
    __tablename__ = "kpi_module"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="模块ID")
    main_id = Column(
        Integer, ForeignKey("kpi_main.id"), nullable=False, index=True, comment="关联总表ID"
    )
    reliability = Column(DECIMAL(10, 2), nullable=False, comment="可靠性")
    regulationsSafety = Column(DECIMAL(10, 2), nullable=False, comment="法规\安全性")
    comfort = Column(DECIMAL(10, 2), nullable=False, comment="舒适性")
    usability = Column(DECIMAL(10, 2), nullable=False, comment="可用性")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")

    # 反向关联 & 下级关联
    main = relationship("KpiMain", back_populates="module_list")
    kpi_item_list = relationship(
        "KpiItem", back_populates="module", cascade="all, delete-orphan"
    )


# 3. KPI明细项表：kpi_item
class KpiItem(Base):
    __tablename__ = "kpi_item"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="KPI明细ID")
    module_id = Column(
        Integer,
        ForeignKey("kpi_module.id"),
        nullable=False,
        index=True,
        comment="关联模块表ID",
    )
    KPIType = Column(String(64), nullable=False, comment="KPI项")
    KPICount = Column(Integer, default=0, comment="KPI事件次数")
    MPI = Column(Integer, default=0, comment="MPI")
    RawScore = Column(DECIMAL(8, 2), nullable=False, comment="原始得分（按每小项100分计）")
    KPIScore = Column(DECIMAL(8, 2), nullable=False, comment="加权得分（最终得分）")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")

    module = relationship("KpiModule", back_populates="kpi_item_list")
