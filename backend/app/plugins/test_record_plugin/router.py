from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.plugins.test_record_plugin import schemas, services
import os

router = APIRouter()

# 1. 创建单条记录
@router.post("/", response_model=schemas.TestRecord)
def create_record(record: schemas.TestRecordCreate, db: Session = Depends(get_db)):
    return services.create_test_record(db=db, record=record)

# 2. 获取列表
@router.get("/", response_model=list[schemas.TestRecord])
def get_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return services.get_test_records(db, skip=skip, limit=limit)

# 3. 获取单条详情
@router.get("/{record_id}", response_model=schemas.TestRecord)
def get_record(record_id: int, db: Session = Depends(get_db)):
    return services.get_test_record(db, record_id=record_id)

# 4. 更新
@router.put("/{record_id}", response_model=schemas.TestRecord)
def update_record(record_id: int, record: schemas.TestRecordUpdate, db: Session = Depends(get_db)):
    return services.update_test_record(db, record_id=record_id, record=record)

# 5. 删除
@router.delete("/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    services.delete_test_record(db, record_id=record_id)
    return {"msg": "删除成功"}

# 6. 批量本地数据导入（核心功能）
@router.post("/batch_import")
def batch_import(
    # data: schemas.TestRecordBatchImport,
    path: str = Query(..., description="Excel文件的本地绝对路径"),
    db: Session = Depends(get_db)
):

    """
    批量本地数据导入
    请求体：{"records": [测试记录对象1, 测试记录对象2...]}
    """
    # return services.batch_import_records(db, data.records)
    return services.batch_import_records(path,db)