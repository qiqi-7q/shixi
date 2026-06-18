from typing import Optional

from fastapi import File, Form, UploadFile
import aiofiles
from app.core.config import settings
from app.core.redis_client import redisserve

# 上传目录
TEMP_DIR = settings.UPLOAD_DIR / "temp"

# # 允许的文件格式
# ALLOWED_EXT = {"jpg", "jpeg", "png", "gif", "pdf", "txt", "doc", "docx"}


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
    if final_path.exists():
        for p in chunk_dir.iterdir():
            p.unlink(missing_ok=True)
        chunk_dir.rmdir()
        return {
            "code": 200,
            "message": "文件已合并完成",
            "file_url": f"/uploads/{SET_DIR}/{file.filename}",
            "merged": True,
        }

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
                }

        # 原子 rename 到最终位置
        upload_dir.mkdir(parents=True, exist_ok=True)
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
