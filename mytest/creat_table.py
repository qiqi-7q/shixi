import pymysql
from pymysql.err import OperationalError, ProgrammingError

# ===================== MySQL 配置（请改成你自己的）=====================
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "shang"
MYSQL_DB = "data_platform_test"
# ======================================================================

def create_test_records_table():
    """自动创建测试记录表 test_records"""
    try:
        # 1. 连接数据库
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            charset="utf8mb4"
        )
        cursor = conn.cursor()

        # 2. 建表 SQL（和你需求完全一致）
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS `test_records` (
          `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
          `project` varchar(100) NOT NULL COMMENT '项目',
          `car_type` varchar(100) NOT NULL COMMENT '车型',
          `function_mode` varchar(100) DEFAULT NULL COMMENT '功能模式',
          `problem_desc` text COMMENT '问题描述',
          `problem_category` varchar(100) DEFAULT NULL COMMENT '问题分类',
          `problem_phenomenon` varchar(100) DEFAULT NULL COMMENT '问题现象',
          `takeover_type` varchar(100) DEFAULT NULL COMMENT '接管类型',
          `problem_time` datetime NOT NULL COMMENT '问题时间',
          `vin_code` varchar(50) NOT NULL COMMENT '车辆VIN号',
          `data_link` varchar(500) DEFAULT NULL COMMENT '数据链接',
          `wetrack_link` varchar(500) DEFAULT NULL COMMENT 'Wetrack链接',
          `analyze_result` text COMMENT '分析结果',
          `analyze_user` varchar(50) DEFAULT NULL COMMENT '分析人员',
          `analyze_attach` varchar(500) DEFAULT NULL COMMENT '分析附件',
          `software_version` varchar(50) DEFAULT NULL COMMENT '软件版本',
          `remarks` text COMMENT '备注',
          `custom_fields` json DEFAULT NULL COMMENT '自定义扩展字段',
          `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
          `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
          PRIMARY KEY (`id`),
          KEY `idx_vin` (`vin_code`),
          KEY `idx_problem_time` (`problem_time`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测试记录表';
        """

        # 3. 执行建表
        cursor.execute(create_table_sql)
        conn.commit()
        print("✅ 数据表 test_records 创建成功！")

    except OperationalError as e:
        print(f"❌ 数据库连接失败：{e}")
    except ProgrammingError as e:
        print(f"❌ SQL 执行错误：{e}")
    finally:
        if 'conn' in locals() and conn.open:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_test_records_table()