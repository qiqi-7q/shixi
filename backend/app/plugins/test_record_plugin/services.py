from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.plugins.test_record_plugin import models, schemas
from typing import List


# 创建
def create_test_record(db: Session, record: schemas.TestRecordCreate):
    db_record = models.TestRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


# 获取列表
def get_test_records(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TestRecord).offset(skip).limit(limit).all()


# 获取单条
def get_test_record(db: Session, record_id: int):
    record = db.query(models.TestRecord).filter(models.TestRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


# 更新
def update_test_record(db: Session, record_id: int, record: schemas.TestRecordUpdate):
    db_record = db.query(models.TestRecord).filter(models.TestRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")

    update_data = record.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)

    db.commit()
    db.refresh(db_record)
    return db_record


# 删除
def delete_test_record(db: Session, record_id: int):
    record = db.query(models.TestRecord).filter(models.TestRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(record)
    db.commit()
    return True


# 批量导入
def batch_import_records(db: Session, records: List[schemas.TestRecordCreate]):
    if not records:
        raise HTTPException(status_code=400, detail="导入数据不能为空")

    success_count = 0
    for item in records:
        try:
            db_record = models.TestRecord(**item.dict())
            db.add(db_record)
            success_count += 1
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"导入失败：{str(e)}")

    db.commit()
    return {
        "msg": "批量导入完成",
        "total": len(records),
        "success": success_count
    }