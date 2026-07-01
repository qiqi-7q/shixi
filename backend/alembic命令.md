修改模型后，如果当前在backend文件夹内，执行命令(alembic.ini在backend文件夹下)：
alembic revision --autogenerate -m "备注"
alembic upgrade head

修改模型后，如果当前不在backend文件夹内，执行命令(alembic.ini在backend文件夹下)：
alembic -c backend/alembic.ini revision --autogenerate -m "xxx"
alembic -c backend/alembic.ini upgrade head

alembic init alembic   # 初始化命令（首次创建迁移环境）


# 升级到指定版本ID
alembic upgrade 版本id

# 只升级1个版本
alembic upgrade +1

# 回退上1个版本
alembic downgrade -1

# 回退到指定历史版本（该版本之后所有变更全部撤销）
alembic downgrade 41e4327860a5

# 回退到初始空库（谨慎！开发环境使用）
alembic downgrade base

# 查看当前数据库生效的版本
alembic current

# 查看完整版本历史链条（所有迁移ID+备注）
alembic history

# 简化输出历史（只打印版本ID）
alembic history --verbose