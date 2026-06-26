import enum
from sqlalchemy import Column, DECIMAL, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base

# 中间关联表：测试路线与特征的多对多关系
# test_route_features = Table(
#     "test_route_features",
#     Base.metadata,
#     Column("id", Integer, primary_key=True, index=True, comment="主键ID"),
#     Column("test_route_id", Integer, ForeignKey("test_routes.id"), nullable=False, comment="测试路线ID"),
#     Column("route_feature_id", Integer, ForeignKey("route_features.id"), nullable=False, comment="路线特征ID"),
# )
# class RouteFeature(str, enum.Enum):
#     """路线特征"""

#     A = "可靠性"  # 可靠性
#     B = "法规/安全性"  # 法规/安全性
#     C = "舒适性"  # 舒适性
#     D = "可用性"  # 可用性

class TestRoute(Base):
    __tablename__ = "test_routes"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    location = Column(String(100), comment="城市")
    route_name = Column(String(100), nullable=False, comment="路线名称")
    route_length = Column(DECIMAL(10, 1), nullable=False, comment="路线里程")
    diff = Column(DECIMAL(3, 0), nullable=False, comment="难度系数（0-100）")
    test_func = Column(String(100), nullable=False, comment="测试功能")
    route_desc = Column(Text, comment="路线描述")
    route_feature = Column(String(100), comment="路线特征")
    route_link = Column(String(500), comment="路线链接")
    remark = Column(Text, comment="备注")

    # 多对多关联：路线特征
    # routefeatures = relationship("RouteFeature", secondary=test_route_features, back_populates="test_routes")

    creator = Column(String(50), nullable=False, comment="创建人")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )


# class RouteFeature(Base):
#     __tablename__ = "route_features"
#
#     id = Column(Integer, primary_key=True, index=True, comment="主键ID")
#     feature_name = Column(String(100), nullable=False, comment="特征名称")
#
#     # 多对多关联：测试路线
#     test_routes = relationship("TestRoute", secondary=test_route_features, back_populates="routefeatures")
