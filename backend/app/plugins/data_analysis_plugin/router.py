from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.plugins.data_analysis_plugin.services import dataAnalysis
from app.plugins.data_analysis_plugin.schemas import UpdateSuccessRateRequest

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
    # 将 SQLAlchemy 对象转换为可序列化的字典
    data = []
    for record in records:
        data.append({
            "id": record.id,
            "project": record.project,
            "carModel": record.carModel,
            "version": record.version,
            "funcMode": record.funcMode,
            "kpiMileage": float(record.kpiMileage),
            "totalScore": float(record.totalScore),
            "createTime": record.createTime.isoformat() if record.createTime else None,
            "updateTime": record.updateTime.isoformat() if record.updateTime else None,
        })
    return {"message": "success", "code": 200, "data": data, "total": total_count}


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

# ==================== 可视化统计接口 ====================
@router.get("/stats/overview")
async def get_analysis_overview_route(
    db: AsyncSession = Depends(get_db),
    project: Optional[str] = Query(None, description="项目筛选（模糊匹配）"),
    carModel: Optional[str] = Query(None, description="车型筛选"),
    funcMode: Optional[str] = Query(None, description="功能模式筛选"),
):
    """获取分析数据总览统计：总记录数、平均KPI里程、平均总分、最高总分"""
    result = await dataAnalysis.get_analysis_overview(
        db, project=project, carModel=carModel, funcMode=funcMode
    )
    return {"code": 200, "data": result, "message": "获取分析数据总览成功"}


@router.get("/stats/projects")
async def get_projects_route(db: AsyncSession = Depends(get_db)):
    """获取所有项目名称列表"""
    result = await dataAnalysis.get_projects(db)
    return {"code": 200, "data": {"projects": result}, "message": "获取项目列表成功"}


@router.get("/stats/version")
async def get_version_stats_route(
    db: AsyncSession = Depends(get_db),
    project: Optional[str] = Query(None, description="项目名称（精确匹配）"),
    carModel: Optional[str] = Query(None, description="车型筛选"),
    funcMode: Optional[str] = Query(None, description="功能模式筛选"),
):
    """获取版本得分统计（可按项目名称筛选）"""
    result = await dataAnalysis.get_version_stats(
        db, project=project, carModel=carModel, funcMode=funcMode
    )
    return {
        "code": 200,
        "data": {"version_stats": result},
        "message": "获取版本得分统计成功",
    }

@router.put("/update_success_rate")
async def update_success_rate(
    request: UpdateSuccessRateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    手动更新NAP成功率指标并重新计算KPI得分
    
    支持用户在前端输入以下指标（0-100的百分比）：
    - 变道成功率
    - 汇入成功率
    - 汇出成功率
    - 分合流成功率
    - 特殊场景成功率
    - 限速识别成功率
    
    更新范围：kpi_item、kpi_main、kpi_module 三个表的得分都会更新
    """
    result = await dataAnalysis.update_success_rate(
        db=db,
        project=request.project,
        model=request.carModel,
        version=request.version,
        funcMode=request.funcMode,
        change_lane_success_rate=request.change_lane_success_rate,
        inflow_success_rate=request.inflow_success_rate,
        outflow_success_rate=request.outflow_success_rate,
        diverge_converge_rate=request.diverge_converge_rate,
        special_rate=request.special_rate,
        recog_rate=request.recog_rate,
    )
    if result == "success":
        return {"message": "成功率指标更新成功", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}
