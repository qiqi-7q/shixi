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
        test_func: Optional[str] = None,
        diff: Optional[int] = None,
        location: Optional[str] = None,
        order_by_length: Optional[str] = None,
    ) -> dict:
        stmt = select(models.TestRoute)

        # 筛选条件
        if location:
            stmt = stmt.filter(models.TestRoute.location.contains(location))
        if test_func:
            stmt = stmt.filter(models.TestRoute.test_func.contains(test_func))
        if diff is not None:
            stmt = stmt.filter(models.TestRoute.diff == diff)

        # 统计总数
        from sqlalchemy import func

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        # 排序
        if order_by_length == "asc":
            stmt = stmt.order_by(models.TestRoute.route_length.asc())
        elif order_by_length == "desc":
            stmt = stmt.order_by(models.TestRoute.route_length.desc())
        else:
            stmt = stmt.order_by(models.TestRoute.id.desc())

        # 分页查询
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        items = list(result.scalars().all())

        return {"items": items, "total": total, "skip": skip, "limit": limit}

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
