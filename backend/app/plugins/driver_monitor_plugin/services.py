from datetime import date
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_,or_
from fastapi import HTTPException
from app.plugins.driver_monitor_plugin import models, schemas

class DriverMonitorService:
    # 创建
    @staticmethod
    def create_driver_monitor(db: Session, monitor: schemas.DriverMonitorCreate):
        db_monitor = models.DriverMonitor(**monitor.model_dump())
        db.add(db_monitor)
        db.commit()
        db.refresh(db_monitor)
        return db_monitor


    # 获取列表
    @staticmethod
    def get_driver_monitors(db: Session, skip: int = 0, limit: int = 100,
                            driver_name: Optional[str] = None, vin_code: Optional[str] = None,
                            test_start_date: Optional[date] = None,
                            test_end_date: Optional[date] = None):
        query = db.query(models.DriverMonitor)
        if driver_name:
            query = query.filter(models.DriverMonitor.driver_name == driver_name)
        if vin_code:
            query = query.filter(models.DriverMonitor.vin_code == vin_code)
        if test_start_date:
            query = query.filter(models.DriverMonitor.test_start_date >= test_start_date)
        if test_end_date:
            query = query.filter(models.DriverMonitor.test_end_date <= test_end_date)
        return query.offset(skip).limit(limit).all()


    # 获取单条
    @staticmethod
    def get_driver_monitor(db: Session, monitor_id: int):
        monitor = db.query(models.DriverMonitor).filter(models.DriverMonitor.id == monitor_id).first()
        if not monitor:
            raise HTTPException(status_code=404, detail="记录不存在")
        return monitor


    # 更新
    @staticmethod
    def update_driver_monitor(db: Session, monitor_id: int, monitor: schemas.DriverMonitorUpdate):
        db_monitor = db.query(models.DriverMonitor).filter(models.DriverMonitor.id == monitor_id).first()
        if not db_monitor:
            raise HTTPException(status_code=404, detail="记录不存在")

        update_data = monitor.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_monitor, key, value)

        db.commit()
        db.refresh(db_monitor)
        return db_monitor


    # 删除
    @staticmethod
    def delete_driver_monitor(db: Session, monitor_id: int):
        monitor = db.query(models.DriverMonitor).filter(models.DriverMonitor.id == monitor_id).first()
        if not monitor:
            raise HTTPException(status_code=404, detail="记录不存在")
        db.delete(monitor)
        db.commit()
        return True

