from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")

    name = Column(String(100), nullable=False, index=True, comment="姓名")
    contact_engineer = Column(String(100), comment="对接工程师")
    third_party_company = Column(String(200), index=True, comment="第三方公司")
    contact_info = Column(String(200), comment="联系方式")
    remarks = Column(Text, comment="备注")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
