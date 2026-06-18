import json

from typing import Dict, Any, Optional

from app.core.config import settings
from app.core.redis_client import redisserve
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.upload_files import upload_file
from app.core.database import get_db
from app.plugins.project_plan_plugin.services import plan_serve

router = APIRouter()


task_filter = ["电子内部发测", "整车发测"]
cell_filter = ["SOP", "OTA"]


@router.post("/create_plan")
async def create_plan(
    # 项目进度表文件路径
    file_path: str,
) -> Dict[str, Any] | str:
    """创建项目计划"""
    # 生成Redis键
    plan_key = f"project_plan:{file_path}"
    # 先从Redis获取数据，如果存在则直接返回数据
    plan_data = await redisserve.get_data(plan_key)
    if plan_data:
        return {"message": "数据已存在", "code": 200, "data": json.loads(plan_data)}
    data = await plan_serve.async_parse_program_plan(
        file_path, task_filter=task_filter, cell_filter=cell_filter
    )
    if isinstance(data, str):
        return {"message": data, "code": 400, "data": None}
    # 解析成功，将数据存储到Redis，过期时间为20分钟
    await redisserve.set_data(plan_key, json.dumps(data), expire_seconds=60 * 20)
    return {"message": "解析成功", "code": 200, "data": data}


@router.post("/upload_planfile")
async def upload_planfile(
    file: UploadFile = File(...),
    fileMd5: str = Form(...),
    chunkIndex: Optional[int] = Form(...),
    totalChunk: Optional[int] = Form(...),
    totalSize: Optional[int] = Form(...),
) -> Dict[str, Any] | str:
    """上传项目计划文件"""
    # 允许的文件格式
    ALLOWED_EXT = {".xlsx", ".xls"}
    SET_DIR = "project_plan"

    return await upload_file(
        file, fileMd5, chunkIndex, totalChunk, totalSize, ALLOWED_EXT, SET_DIR
    )
