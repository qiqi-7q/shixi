from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.plugins.test_route_plugin import schemas, services

router = APIRouter()


# 1. 创建单条路线
@router.post("/createroute")
async def create_route(
    route: schemas.TestRouteCreate, db: AsyncSession = Depends(get_db)
):
    result = await services.TestRouteService.create_test_route(db=db, route=route)
    if result == "success":
        return {"message": "路线创建成功", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}


# 2. 获取路线列表
@router.get("/fixsearch")
async def get_routes_simple(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    test_func: Optional[str] = None,
    diff: Optional[int] = None,
    location: Optional[str] = None,
    order_by_length: Optional[str] = None
):
    result = await services.TestRouteService.get_test_routes_simple(
        db,
        skip=skip,
        limit=limit,
        test_func=test_func,
        diff=diff,
        location=location,
        order_by_length=order_by_length,
    )
    return {"data": result, "code": 200, "message": "success"}


# 3. 获取单条路线详情
@router.get("/getroute/{route_id}")
async def get_route(route_id: int, db: AsyncSession = Depends(get_db)):
    result = await services.TestRouteService.get_test_route(db, route_id=route_id)
    if isinstance(result, str):
        return {"data": None, "message": result, "code": 400}
    return {"data": result, "code": 200, "message": "success"}


# 4. 更新路线
@router.put("/updateroute/{route_id}")
async def update_route(
    route_id: int, route: schemas.TestRouteUpdate, db: AsyncSession = Depends(get_db)
):
    result = await services.TestRouteService.update_test_route(
        db, route_id=route_id, route=route
    )
    if result == "success":
        return {"message": "路线更新成功", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}


# 5. 删除路线
@router.delete("/delroute/{route_id}")
async def delete_route(route_id: int, db: AsyncSession = Depends(get_db)):
    result = await services.TestRouteService.delete_test_route(db, route_id=route_id)
    if result == "success":
        return {"message": "路线删除成功", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}
