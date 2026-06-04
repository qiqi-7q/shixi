from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.plugins.driver_monitor_plugin import schemas, services
import os

router = APIRouter()

# 1. 创建单条记录
@router.post("/", response_model=schemas.DriverMonitorCreate)
def create_monitor(monitor: schemas.DriverMonitorCreate, db: Session = Depends(get_db)):
    return services.DriverMonitorService.create_driver_monitor(db=db, monitor=monitor)

# 2. 获取列表
@router.get("/", response_model=list[schemas.DriverMonitorResponse])
def get_monitors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                 driver_name: Optional[str] = None, vin_code: Optional[str] = None,
                 test_start_date: Optional[date] = None,
                 test_end_date: Optional[date] = None):
    return services.DriverMonitorService.get_driver_monitors(db, skip=skip, limit=limit,
                                                             driver_name=driver_name, vin_code=vin_code,
                                                             test_start_date=test_start_date,
                                                             test_end_date=test_end_date)

# 3. 获取单条详情
@router.get("/{monitor_id}", response_model=schemas.DriverMonitorResponse)
def get_monitor(monitor_id: int, db: Session = Depends(get_db)):
    return services.DriverMonitorService.get_driver_monitor(db, monitor_id=monitor_id)

# 4. 更新
@router.put("/{monitor_id}", response_model=schemas.DriverMonitorResponse)
def update_monitor(monitor_id: int, monitor: schemas.DriverMonitorUpdate, db: Session = Depends(get_db)):
    return services.DriverMonitorService.update_driver_monitor(db, monitor_id=monitor_id, monitor=monitor)

# 5. 删除
@router.delete("/{monitor_id}")
def delete_monitor(monitor_id: int, db: Session = Depends(get_db)):
    services.DriverMonitorService.delete_driver_monitor(db, monitor_id=monitor_id)
    return {"msg": "删除成功"}
