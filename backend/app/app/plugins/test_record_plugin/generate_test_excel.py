from openpyxl import Workbook

# 创建工作簿
wb = Workbook()
ws = wb.active
ws.title = "测试记录"

# 表头
headers = [
    'project', 'car_type', 'function_mode', 'problem_desc', 'problem_category',
    'kpi_type', 'problem_scene', 'problem_type', 'problem_phenomenon',
    'takeover_type', 'problem_time', 'vin_code', 'data_link', 'wetrack_link',
    'analyze_result', 'analyze_user', 'software_version', 'remarks'
]

# 添加表头
ws.append(headers)

# 测试数据
test_data = [
    [
        'ADAS测试', 'C11', 'NAP', '高速行驶时突然退出NAP模式', 'RELIABILITY',
        'EXIT', '高速公路', '异常退出', '突然退出', '驾驶员接管',
        '2024-01-15 14:30:00', 'LSVAU218XMN123456',
        'http://data.example.com/1', 'http://wetrack.example.com/1',
        '已分析', '张三', 'V1.0', '测试数据1'
    ],
    [
        'ADAS测试', 'T03', 'NAP', '匝道汇入时变道失败', 'USABILITY',
        'CHANGELANE_F', '匝道', '变道问题', '变道失败', '系统接管',
        '2024-01-16 09:15:00', 'LSVAU218XMN123457',
        'http://data.example.com/2', 'http://wetrack.example.com/2',
        '待分析', '李四', 'V1.0', '测试数据2'
    ],
    [
        '智能座舱', 'C11', 'HMI', '中控屏幕卡顿', 'COMFORT',
        'EXCEPTION', '城市道路', '系统异常', '屏幕卡顿', '无',
        '2024-01-17 16:45:00', 'LSVAU218XMN123458',
        'http://data.example.com/3', 'http://wetrack.example.com/3',
        '已分析', '张三', 'V2.0', '测试数据3'
    ],
    [
        '底盘测试', 'T03', 'SUSP', '悬挂系统异响', 'COMFORT',
        'VERTICAL', '颠簸路面', '舒适性问题', '异响', '无',
        '2024-01-18 11:20:00', 'LSVAU218XMN123459',
        'http://data.example.com/4', 'http://wetrack.example.com/4',
        '待分析', '李四', 'V1.0', '测试数据4'
    ]
]

# 添加数据
for row in test_data:
    ws.append(row)

# 保存文件
output_path = r'C:\Users\2645227\project\lpATMP\backend\app\plugins\test_record_plugin\test_records.xlsx'
wb.save(output_path)

print(f'Excel文件已生成: {output_path}')
print(f'共 {len(test_data)} 条测试记录')
