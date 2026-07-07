import asyncio
from typing import Optional
from typing import Optional, List
from fastapi import APIRouter, File, Form, UploadFile
import aiofiles
from minio import S3Error
from starlette.responses import StreamingResponse

from app.core.config import settings
from app.core.redis_client import redisserve
from app.core.minio_client import minioserve

# 上传目录
TEMP_DIR = settings.UPLOAD_DIR / "temp"

# # 允许的文件格式
# ALLOWED_EXT = {"jpg", "jpeg", "png", "gif", "pdf", "txt", "doc", "docx"}

upload_router = APIRouter(prefix="/upload", tags=["通用文件上传"])


async def upload_file(
    file: UploadFile = File(...),
    fileMd5: str = Form(...),
    chunkIndex: Optional[int] = Form(...),
    totalChunk: Optional[int] = Form(...),
    totalSize: Optional[int] = Form(...),
    ALLOWED_EXT: set = None,
    SET_DIR: str = None,
):
    """分片上传接口"""
    # 文件格式校验
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    print(f"file: {file.filename}, ext: {ext}")
    if "." + ext not in ALLOWED_EXT:
        return {"code": 400, "message": f"仅支持{','.join(ALLOWED_EXT)}格式文件"}

    # 上传目录
    upload_dir = settings.UPLOAD_DIR / SET_DIR

    # 创建临时分片目录（按 fileMd5 隔离）
    chunk_dir = TEMP_DIR / fileMd5
    chunk_dir.mkdir(parents=True, exist_ok=True)

    # 保存当前分片
    chunk_path = chunk_dir / f"chunk_{chunkIndex}"
    async with aiofiles.open(chunk_path, "wb") as f:
        while data := await file.read(1024 * 1024):
            await f.write(data)

    # 收集已上传分片索引
    uploaded = sorted(int(p.name.split("_", 1)[1]) for p in chunk_dir.iterdir())

    if len(uploaded) < totalChunk:
        return {
            "code": 200,
            "message": f"分片 {chunkIndex} 上传成功",
            "uploaded": uploaded,
            "merged": False,
        }

    # 所有分片到齐，检查是否已合并完成
    final_path = upload_dir / file.filename

    # 获取 Redis 分布式锁，协调多进程/多协程并发
    lock_key = f"upload:merge:{fileMd5}"
    client_id = await redisserve.acquire_lock(lock_key, expire_seconds=30)
    if client_id is None:
        return {
            "code": 200,
            "message": f"分片 {chunkIndex} 上传成功，其他进程合并中",
            "uploaded": uploaded,
            "merged": False,
        }

    try:
        # 删除Redis中对应的键
        await redisserve.delete_data(f"project_plan:{file.filename}")
        # 双重检查（锁内重新统计，防止分片在等锁期间被清理）
        uploaded = sorted(int(p.name.split("_", 1)[1]) for p in chunk_dir.iterdir())
        if len(uploaded) < totalChunk:
            return {
                "code": 200,
                "message": f"分片 {chunkIndex} 上传成功",
                "uploaded": uploaded,
                "merged": False,
            }

        # 用临时文件 + "xb" 独占创建，文件系统级别保护
        tmp_path = chunk_dir / f"{file.filename}.tmp"
        async with aiofiles.open(tmp_path, "xb") as out:
            total_written = 0
            for idx in uploaded:
                cp = chunk_dir / f"chunk_{idx}"
                async with aiofiles.open(cp, "rb") as cf:
                    while data := await cf.read(1024 * 1024):
                        await out.write(data)
                        total_written += len(data)

            # 校验总大小
            if total_written != totalSize:
                tmp_path.unlink()
                return {
                    "code": 400,
                    "message": f"文件大小校验失败，期望 {totalSize} 字节，实际 {total_written} 字节",
                    "data": None,
                }

        # 覆盖已有同名文件，再原子 rename 到最终位置
        upload_dir.mkdir(parents=True, exist_ok=True)
        final_path.unlink(missing_ok=True)
        tmp_path.rename(final_path)

        # 清理临时分片
        for p in chunk_dir.iterdir():
            p.unlink()
        chunk_dir.rmdir()

        return {
            "code": 200,
            "message": "文件上传并合并完成",
            "file_url": f"/uploads/{SET_DIR}/{file.filename}",
            "merged": True,
            "data": None,
        }

    except FileExistsError:
        return {
            "code": 200,
            "message": f"分片 {chunkIndex} 上传成功，合并中",
            "uploaded": uploaded,
            "merged": False,
        }

    finally:
        await redisserve.lua_script(lock_key, client_id)


async def upload_files_general(
    files,
    table_name: str,
    record_id: int,
    ALLOWED_EXT: set = None,
    start_index: int = 1,
    overwrite: bool = False,
):
    """
    通用批量上传文件接口（存储到MinIO）
    文件存储路径：{table_name}_files/{record_id}/{record_id}_01, {record_id}_02, ...
    :param files: UploadFile列表
    :param table_name: 表名，用于创建目录
    :param record_id: 记录ID
    :param ALLOWED_EXT: 允许的文件扩展名集合
    :param start_index: 起始索引（仅在 overwrite=True 或目录为空时生效）
    :param overwrite: 是否覆盖所有旧文件并重新编号（True=从_01开始，False=从最大索引继续）
    :return: 文件URL列表
    """
    import re

    prefix = f"test/{table_name}_files/{record_id}"

    try:
        if overwrite:
            objects = await asyncio.to_thread(minioserve.list_objects, prefix=prefix)
            for obj in objects:
                await asyncio.to_thread(minioserve.delete_file, obj.object_name)
            current_max_idx = start_index - 1
        else:
            current_max_idx = start_index - 1
            objects = await asyncio.to_thread(minioserve.list_objects, prefix=prefix)
            pattern = re.compile(rf"^{prefix}/{record_id}_(\d{{2}})")
            for obj in objects:
                match = pattern.match(obj.object_name)
                if match:
                    idx = int(match.group(1))
                    if idx > current_max_idx:
                        current_max_idx = idx

        saved_paths = []
        for offset, file in enumerate(files):
            if not file or not file.filename:
                continue

            ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
            if ALLOWED_EXT and "." + ext not in ALLOWED_EXT:
                continue

            content = await file.read()
            if not content:
                continue

            idx = current_max_idx + offset + 1
            new_filename = (
                f"{record_id}_{idx:02d}.{ext}" if ext else f"{record_id}_{idx:02d}"
            )
            object_name = f"{prefix}/{new_filename}"

            content_type = get_content_type(ext)
            url = await asyncio.to_thread(
                minioserve.upload_file, content, object_name, content_type=content_type
            )

            saved_paths.append(url)

        return saved_paths
    except Exception as e:
        raise Exception(f"文件上传到MinIO失败: {str(e)}")


def get_content_type(ext: str) -> str:
    content_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "bmp": "image/bmp",
        "webp": "image/webp",
        "pdf": "application/pdf",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xls": "application/vnd.ms-excel",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "txt": "text/plain",
        "json": "application/json",
        "xml": "application/xml",
        "zip": "application/zip",
        "rar": "application/x-rar-compressed",
        "7z": "application/x-7z-compressed",
    }
    return content_types.get(ext, "application/octet-stream")


@upload_router.post("/{table_name}/{record_id}")
async def upload_files_universal(
    table_name: str,
    record_id: int,
    files: List[UploadFile] = File(..., description="文件列表"),
    overwrite: bool = Form(False, description="是否覆盖旧文件，默认false"),
):
    """
    通用文件上传接口（全局路由）
    文件存储路径：{table_name}_files/{record_id}/{record_id}_01, {record_id}_02, ...

    :param table_name: 表名，用于创建目录
    :param record_id: 记录ID
    :param files: 文件列表
    :param overwrite: 是否覆盖旧文件
    """
    valid_files = [f for f in files if f and f.filename]
    if not valid_files:
        return {"message": "请选择要上传的文件", "code": 400, "data": None}

    saved_paths = await upload_files_general(
        valid_files, table_name, record_id, start_index=1, overwrite=overwrite
    )

    return {
        "message": f"成功上传{len(saved_paths)}个文件",
        "code": 200,
        "data": {
            "record_id": record_id,
            "uploaded_files": saved_paths,
            "total_count": len(saved_paths),
        },
    }



@upload_router.get("/preview")
async def preview_file(
    bucket: str,
    key: str,
    # current_user: User = Depends(get_current_user)
):
    # 前端会返回[f"{bucket},{object_name}",f"{bucket},{object_name}",f"{bucket},{object_name}"]结构的数据
    stream = None
    try:
        obj_stat = minioserve.client.stat_object(bucket,key )
        stream = minioserve.client.get_object(bucket, key)
        return StreamingResponse(content=stream, media_type=obj_stat.content_type)
    except S3Error:
        return {"message": "文件不存在", "code": 404, "data": None}
    finally:
        if stream is not None:
            stream.close()