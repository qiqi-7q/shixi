from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_,or_
from fastapi import HTTPException
from app.plugins.test_route_plugin import models, schemas
from typing import List, Set, Tuple, Optional


class TestRouteService:
    # 创建
    @staticmethod
    def create_test_route(db: Session, route: schemas.TestRouteCreate) -> models.TestRoute:
        db_route = models.TestRoute(**route.model_dump())
        db.add(db_route)
        db.commit()
        db.refresh(db_route)
        return db_route


    # 获取列表
    @staticmethod
    def get_test_routes(db: Session, skip: int = 0, limit: int = 100,
                        route_name: Optional[str] = None, route_desc: Optional[str] = None,
                        route_feature: Optional[str] = None, min_length: Optional[int] = None,
                        max_length: Optional[int] = None)-> List[models.TestRoute]:
        query = db.query(models.TestRoute)
        if route_name:
            query = query.filter(models.TestRoute.route_name.contains(route_name))
        if route_desc:
            query = query.filter(models.TestRoute.route_desc.contains(route_desc))
        if min_length:
            query = query.filter(models.TestRoute.route_length >= min_length)
        if max_length:
            query = query.filter(models.TestRoute.route_length <= max_length)
        if route_feature:
            query = query.filter(models.TestRoute.route_feature.contains(route_feature))
        return query.offset(skip).limit(limit).all()


    # 获取单条
    @staticmethod
    def get_test_route(db: Session, route_id: int) -> models.TestRoute:
        route = db.query(models.TestRoute).filter(models.TestRoute.id == route_id).first()
        if not route:
            raise HTTPException(status_code=404, detail="路线不存在")
        return route


    # 更新
    @staticmethod
    def update_test_route(db: Session, route_id: int, route: schemas.TestRouteUpdate):
        db_route = db.query(models.TestRoute).filter(models.TestRoute.id == route_id).first()
        if not db_route:
            raise HTTPException(status_code=404, detail="路线不存在")

        update_data = route.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_route, key, value)

        db.commit()
        db.refresh(db_route)
        return db_route


    # 删除
    @staticmethod
    def delete_test_route(db: Session, route_id: int):
        route = db.query(models.TestRoute).filter(models.TestRoute.id == route_id).first()
        if not route:
            raise HTTPException(status_code=404, detail="路线不存在")
        db.delete(route)
        db.commit()
        return True