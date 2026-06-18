from openpyxl import load_workbook


def is_empty_row(row_cells) -> bool:
    """
    判断一行是否为全空行
    :param row_cells: Excel行的单元格列表
    :return: True=全空行，False=有有效内容
    """
    for cell in row_cells:
        cell_value = cell.value
        # 处理空值、空字符串、全空白字符
        if cell_value is None:
            continue
        if isinstance(cell_value, str) and cell_value.strip() == "":
            continue
        # 只要有一个非空单元格，就不是空行
        return False
    # 所有单元格都是空的，判定为空行
    return True


def handle_data(ws):
    # 处理表头：解决空表头、重复表头问题，避免字典key异常
    raw_headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    headers = []
    header_count = {}
    for idx, h in enumerate(raw_headers):
        # 空表头自动重命名
        if h is None:
            h = f"unknown_column_{idx+1}"
        # 重复表头自动加序号
        if h in header_count:
            header_count[h] += 1
            h = f"{h}_{header_count[h]}"
        else:
            header_count[h] = 0
        headers.append(h)

    # 逐行生成字典，所有字典存入列表
    dict_list = []
    # for row in ws.iter_rows(min_row=2):  # 第2行开始为数据行
    #     row_dict = dict(zip(headers, [cell.value for cell in row]))
    #     dict_list.append(row_dict)
    for row in ws.iter_rows(min_row=2):  # 从第2行开始读取业务数据
        # 第一步：先判断是不是全空行，是空行直接跳过
        if is_empty_row(row):
            continue

        # 第二步：非空行，正常处理数据
        row_data = {}
        for idx, header in enumerate(headers):
            if idx >= len(row):
                row_data[header] = None
                continue
            cell_value = row[idx].value

            row_data[header] = cell_value

        dict_list.append(row_data)

    return dict_list, headers


# 读取Excel文件，转为字典列表
def excel_to_dict_list(file_path):
    # 加载Excel文件
    try:
        wb = load_workbook(file_path)
        # 优先读取第一个工作表（兼容不同的sheet名称）
        if wb.sheetnames:
            ws = wb[wb.sheetnames[0]]
        else:
            return "❌ Excel文件中没有工作表"
    except Exception as e:
        return f"❌ 文件读取失败：{e}"
    return ws


def handle_excel_some(file_path):
    ws = excel_to_dict_list(file_path)
    # 检查是否返回了错误信息
    if isinstance(ws, str):
        raise Exception(ws)
    # 处理数据行
    dict_list, headers = handle_data(ws)

    return dict_list, headers


# # 4. 主程序执行
# if __name__ == "__main__":
#
#
#     # 第二步：转为字典列表
#     result_list, headers = excel_to_dict_list('E:\LPATMP\mytest\问题记录表.xlsx')
#
#     # 第三步：结果输出
#     print(f"\n📊 处理完成！共提取 {len(result_list)} 条有6666666666效数据")
#     print(f"📋 表头列表：{headers}")
#
#     # 输出前2条数据示例
#     print("\n📌 前2条数据示例：")
#     for i, item in enumerate(result_list[:2]):
#         print(f"\n第{i+1}条数据：")
#         for key, value in item.items():
#             print(f"  {key}: {value}")
