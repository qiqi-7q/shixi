from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.plugins.test_route_plugin import models, schemas


class TestRouteService:

    # 创建
    @staticmethod
    async def create_test_route(
        db: AsyncSession, route: schemas.TestRouteCreate
    ) -> str:
        if not route.route_name:
            return "route_name is empty"
        if not route.route_length:
            return "route_length is empty"
        if route.route_length <= 0:
            return "route_length must be greater than 0"
        if not route.diff:
            return "diff is empty"
        if route.diff < 0 or route.diff > 5:
            return "diff must be between 0 and 5"
        if not route.test_func:
            return "test_func is empty"
        if not route.creator:
            return "creator is empty"
        db_route = models.TestRoute(**route.model_dump())
        db.add(db_route)
        await db.commit()
        await db.refresh(db_route)
        return "success"

    # 获取列表
    @staticmethod
    async def get_test_routes_simple(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        route_name: Optional[str] = None,
        creator: Optional[str] = None,
        route_desc: Optional[str] = None,
        route_feature: Optional[str] = None,
    ) -> List[models.TestRoute]:
        stmt = select(models.TestRoute)
        if route_name:
            stmt = stmt.filter(models.TestRoute.route_name.contains(route_name))
        if creator:
            stmt = stmt.filter(models.TestRoute.creator.contains(creator))
        if route_desc:
            stmt = stmt.filter(models.TestRoute.route_desc.contains(route_desc))
        if route_feature:
            stmt = stmt.filter(models.TestRoute.route_feature.contains(route_feature))
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    # 获取单条
    @staticmethod
    async def get_test_route(db: AsyncSession, route_id: int) -> models.TestRoute | str:
        route = await db.get(models.TestRoute, route_id)
        if not route:
            return "route not found"
        return route

    # 更新
    @staticmethod
    async def update_test_route(
        db: AsyncSession, route_id: int, route: schemas.TestRouteUpdate
    ) -> bool | str:
        db_route = await db.get(models.TestRoute, route_id)
        if not db_route:
            return "route not found"
        if not route.route_name:
            return "route_name is empty"
        if not route.route_length:
            return "route_length is empty"
        if route.route_length <= 0:
            return "route_length must be greater than 0"
        if not route.diff:
            return "diff is empty"
        if route.diff < 0 or route.diff > 5:
            return "diff must be between 0 and 5"
        if not route.test_func:
            return "test_func is empty"
        if not route.creator:
            return "creator is empty"
        update_data = route.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_route, key, value)

        await db.commit()
        await db.refresh(db_route)
        return "success"

    # 删除
    @staticmethod
    async def delete_test_route(db: AsyncSession, route_id: int) -> str:
        route = await db.get(models.TestRoute, route_id)
        if not route:
            return "route not found"
        await db.delete(route)
        await db.commit()
        return "success"
