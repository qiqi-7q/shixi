from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.plugins.test_record_plugin.test_record_tasks import refresh_data_links_job
from app.plugins.vehicle_plugin.vehicle_tasks import re_vs_task, re_bs_task

job_defaults = {
    "replace_existing": True,
    "coalesce": True,
    "max_instances": 1,
    "misfire_grace_time": 60,
}


# 初始化定时调度器
scheduler = AsyncIOScheduler(job_defaults=job_defaults, timezone="Asia/Shanghai")

# 添加定时任务：每天0点30分刷新一次车辆状态
scheduler.add_job(
    id="refresh_vehicle_status",
    name="定时刷新车辆状态",
    func=re_vs_task,
    replace_existing=True,
    trigger="cron",
    hour="0",
    minute="30",
)

scheduler.add_job(
    id="refresh_borrow_status",
    name="定时刷新借用记录状态",
    func=re_bs_task,
    replace_existing=True,
    trigger="cron",
    hour="1",
    minute="00",
)

# trigger = ("cron",)   #每天0点30分刷新一次车辆状态
# hour = ("0",)
# minute = ("30",)

# trigger = ("cron",) #每两小时整点刷新，固定整点执行（0、2、4…）
# hour = ("*/2",)
# minute = ("00",)

# trigger = ("interval",) #从任务启动时刻算起，每两小时刷新
# hours = (2,)


# 添加定时任务：每2小时刷新一次数据链接
scheduler.add_job(
    func=refresh_data_links_job,
    id="refresh_data_links",  # 任务ID，用于取消任务
    name="定时刷新数据链接",  # 任务名称，用于日志记录
    replace_existing=True,  # 如果存在相同ID的任务，则替换为新任务
    trigger="interval",
    hours=2,
)


# 封装停止调度器函数
def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=True)
        print("APScheduler 已关闭")
