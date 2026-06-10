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
            return "路线名称不能为空"
        if not route.route_length:
            return "路线里程不能为空"
        if route.route_length <= 0:
            return "路线里程必须大于0"
        if not route.diff:
            return "难度系数不能为空"
        if route.diff < 0 or route.diff > 100:
            return "难度系数必须在0到100之间"
        if not route.test_func:
            return "测试功能不能为空"
        if not route.creator:
            return "创建人不能为空"
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
            return "路线不存在"
        return route

    # 更新
    @staticmethod
    async def update_test_route(
        db: AsyncSession, route_id: int, route: schemas.TestRouteUpdate
    ) -> bool | str:
        db_route = await db.get(models.TestRoute, route_id)
        if not db_route:
            return "路线不存在"
        if route.route_length <= 0:
            return "路线里程必须大于0"
        if route.diff < 0 or route.diff > 100:
            return "难度系数必须在0到100之间"
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
            return "路线不存在"
        await db.delete(route)
        await db.commit()
        return "success"
