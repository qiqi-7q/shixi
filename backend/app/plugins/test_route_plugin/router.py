from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy import DECIMAL
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.plugins.test_route_plugin import schemas, services
import os

router = APIRouter()

# 1. 创建单条路线
@router.post("/", response_model=schemas.TestRouteResponse)
def create_route(route: schemas.TestRouteCreate, db: Session = Depends(get_db)):
    return services.TestRouteService.create_test_route(db=db, route=route)

# 2. 获取路线列表
@router.get("/", response_model=list[schemas.TestRouteResponse])
def get_routes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
               route_name: Optional[str] = None,
               route_desc: Optional[str] = None,
               route_feature: Optional[str] = None,
               min_length: Optional[int] = None, max_length: Optional[int] = None):
    return services.TestRouteService.get_test_routes(db, skip=skip, limit=limit, route_name=route_name,
                                    route_desc=route_desc, route_feature=route_feature,
                                                     min_length=min_length, max_length=max_length)

# 3. 获取单条路线详情
@router.get("/{route_id}", response_model=schemas.TestRouteResponse)
def get_route(route_id: int, db: Session = Depends(get_db)):
    return services.TestRouteService.get_test_route(db, route_id=route_id)

# 4. 更新路线
@router.put("/{route_id}", response_model=schemas.TestRouteResponse)
def update_route(route_id: int, route: schemas.TestRouteUpdate, db: Session = Depends(get_db)):
    return services.TestRouteService.update_test_route(db, route_id=route_id, route=route)

# 5. 删除路线
@router.delete("/{route_id}")
def delete_route(route_id: int, db: Session = Depends(get_db)):
    services.TestRouteService.delete_test_route(db, route_id=route_id)
    return {"msg": "删除成功"}
