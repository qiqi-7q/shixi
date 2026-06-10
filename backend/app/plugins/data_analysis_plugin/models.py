import enum

from sqlalchemy import Column,
from sqlalchemy.sql import func

from app.core.database import Base

# 数据统计模型：项目、车型、软件版本、测试功能、评价维度、KPI里程、KPI项、KPI事件发生数、MPI结果、模块得分、加权得分