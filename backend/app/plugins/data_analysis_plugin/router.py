from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.plugins.data_analysis_plugin.services import dataAnalysis

router = APIRouter()

"""
NAP统计函数
支持：
- 线性KPI：传入原始里程/比率（浮点数或百分比字符串如"96.40%"）
- 扣分型KPI：传入字典 {'percent': 95} 直接给百分制，或传入整数（表示默认事件次数），或字典{事件:次数}
- 二分型KPI：传入0/1或布尔值
"""


@router.post("/create_analysis")
async def create_analysis(
    project: str,
    model: str,
    version: str,
    funcMode: str,
    db: AsyncSession = Depends(get_db),
):
    """创建分析数据"""
    result = await dataAnalysis.save_to_db(
        db=db, project=project, model=model, version=version, funcMode=funcMode
    )
    if result == "success":
        return {
            "message": f"项目名为：{project}，车型为：{model}，版本为：{version}，测试功能为：{funcMode} 的分析已完成",
            "code": 200,
            "data": None,
        }
    else:
        return {"message": result, "code": 400, "data": None}


@router.get("/fixsearch")
async def get_analysis_datas(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    project: Optional[str] = None,
    carModel: Optional[str] = None,
    version: Optional[str] = None,
    funcMode: Optional[str] = None,
):
    records, total_count = await dataAnalysis.get_analysis_datas(
        skip=skip,
        limit=limit,
        db=db,
        project=project,
        carModel=carModel,
        version=version,
        funcMode=funcMode,
    )
    return {"message": "success", "code": 200, "data": records, "total": total_count}


@router.get("/get_analysis/{analysis_id}")
async def get_analysis_info(
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取单个分析数据"""
    # {1:2,2:3,4:{},5:{}}
    analysisInfo = await dataAnalysis.get_analysis_info(db, analysis_id)
    if isinstance(analysisInfo, str):
        return {"message": analysisInfo, "code": 400, "data": None}
    return {"data": analysisInfo, "message": "success", "code": 200}


@router.put("/analysis_compare")
async def analysis_compare(
    analysis_id1: int, analysis_id2: int, db: AsyncSession = Depends(get_db)
):
    """对比分析数据"""
    # [{1:2,2:3,4:{},5:{}},{1:2,2:3,4:{},5:{}}]
    result = await dataAnalysis.compare_analysis_data(db, analysis_id1, analysis_id2)
    if isinstance(result, str):
        return {"message": result, "code": 400, "data": None}
    else:
        return {"data": result, "code": 200, "message": "分析对比完成"}


@router.delete("/delete_analysis")
async def delete_analysis(analysis_id: int, db: AsyncSession = Depends(get_db)):
    """删除分析数据"""
    result = await dataAnalysis.delete_analysis_data(db, analysis_id)
    if result == "success":
        return {"message": "分析删除成功", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}
