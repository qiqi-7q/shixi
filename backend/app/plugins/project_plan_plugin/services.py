import os

from openpyxl import load_workbook
from typing import Optional, List, Dict, Any, Tuple
import asyncio
from datetime import datetime

from app.core.config import settings


class ProjectPlanService:

    @staticmethod
    def date_to_week_str(dt: datetime) -> str:
        """
        将日期转换为 "2026.6.W3" 格式
        规则：1-6号是W1，7-14号是W2，15-23号是W3，其余是W4
        """
        day = dt.day
        if 1 <= day <= 6:
            week_num = 1
        elif 7 <= day <= 14:
            week_num = 2
        elif 15 <= day <= 23:
            week_num = 3
        else:
            week_num = 4
        return f"{dt.year}.{dt.month}.W{week_num}"

    @staticmethod
    def week_str_to_comparable(week_str: str) -> Tuple[int, int, int]:
        """
        将 "2026.6.W3" 转换为可比较的元组 (2026, 6, 3)
        """
        year_part, month_part, week_part = week_str.split(".")
        year = int(year_part)
        month = int(month_part)
        week_num = int(week_part.replace("W", ""))
        return (year, month, week_num)

    @staticmethod
    def sort_data_by_week(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        按整车发测的SOP阀点周期排序
        排序规则：
        1. 有整车发测数据：按阀点周期升序（时间越早越靠前）
        2. 无整车发测数据：排在最后
        """

        def get_sort_key(item: Dict[str, Any]) -> Tuple[int, Tuple[int, int, int]]:
            vehicle_data = item.get("整车发测", [])

            # 情况2：无整车发测数据
            if not vehicle_data:
                return (1, (0, 0, 0))

            # 情况1：有整车发测数据，将整车发测数据中的SOP和OTA数据合并取最小，以这个最小值去与其他项目比较
            weeks = vehicle_data.get("SOP", []) + vehicle_data.get("OTA", [])
            # "2026.1.W3" → (2026, 1, 3)
            weeks = [ProjectPlanService.week_str_to_comparable(week) for week in weeks]
            earliest_week = min(weeks)
            return (0, earliest_week)

        return sorted(data, key=get_sort_key)

    @staticmethod
    def parse_program_plan(
        file_path: str,
        task_filter: Optional[List[str]] = None,
        cell_filter: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        解析项目进度表Excel文件，支持任务、单元格内容过滤，按主线分组输出

        Args:
            file_path: Excel文件本地路径
            task_filter: 细分任务白名单过滤器，例：["电子内部发测", "整车发测"]，None则不过滤
            cell_filter: 单元格内容关键词过滤器，例：["SOP", "OTA"]，匹配任意关键词即保留，None则不过滤

        Returns:
            dict: 包含全部数据和未来三个月整车发测任务
            {
                "all_data": [...],
                "upcoming_vehicle_tasks": [...]
            }
        """
        # 只读+仅读取计算值，解决WPS损坏填充样式Fill报错，大文件低内存
        wb = load_workbook(file_path, data_only=True)
        ws = wb.active
        try:
            # ---------------------- 1. 解析阀点周期表头（第1行，C列起） ----------------------
            week_headers: List[Tuple[int, str]] = []
            # 先读取第一行全部单元格，避免read_only下max_column不准
            row1_cells = list(ws.iter_rows(min_row=1, max_row=1, values_only=True))[0]
            for col_idx, raw_val in enumerate(row1_cells, start=1):
                if col_idx < 3:  # C列=3，跳过A/B列表头
                    continue
                if raw_val is None:
                    continue
                clean_val = str(raw_val).strip()
                if clean_val:
                    week_headers.append((col_idx, clean_val))
            if not week_headers:
                return []

            # ---------------------- 2. 预解析所有合并单元格，行号→主线名称映射 ----------------------
            row_to_main: Dict[int, str] = {}
            for merged_range in ws.merged_cells.ranges:
                min_row, min_col, max_row, max_col = merged_range.bounds
                main_raw = ws.cell(row=min_row, column=min_col).value
                if main_raw is None:
                    continue
                # 取第一行文本，去除换行空格
                main_text = str(main_raw).strip().split("\n")[0]
                if not main_text:
                    continue
                # 合并区间所有行绑定主线
                for row_num in range(min_row, max_row + 1):
                    row_to_main[row_num] = main_text

            # ---------------------- 3. 逐行遍历提取业务数据 ----------------------
            main_data: Dict[str, Dict[str, List[Dict[str, str]]]] = {}
            current_main: Optional[str] = None  # 缓存上一行主线，处理非合并行

            # 遍历全部数据行（从第2行开始）
            all_data_rows = list(ws.iter_rows(min_row=2, values_only=True))
            for row_offset, row_cells in enumerate(all_data_rows, start=2):
                # 3.1 获取当前行所属主线
                main_line = row_to_main.get(row_offset)
                if main_line is None:
                    # 非合并单元格，读取A列手动获取主线
                    a_cell_val = row_cells[0]
                    if a_cell_val is not None:
                        clean_a = str(a_cell_val).strip().split("\n")[0]
                        if clean_a:
                            main_line = clean_a
                            current_main = main_line
                        else:
                            main_line = current_main
                    else:
                        main_line = current_main
                # 无主线则跳过该行
                if not main_line:
                    continue

                # 3.2 获取细分任务（B列，索引1）
                task_raw = row_cells[1]
                if task_raw is None:
                    continue
                task_name = str(task_raw).strip()
                if not task_name:
                    continue
                # 任务白名单过滤
                if task_filter is not None and task_name not in task_filter:
                    continue
                # 主线容器初始化
                if main_line not in main_data:
                    main_data[main_line] = {}
                task_group = main_data[main_line]
                if task_name not in task_group:
                    task_group[task_name] = []

                # 3.3 遍历所有阀点周期列，读取单元格值并过滤
                for col_num, week_name in week_headers:
                    cell_raw = ws.cell(row=row_offset, column=col_num).value
                    if cell_raw is None:
                        continue
                    cell_text = str(cell_raw).strip()
                    if not cell_text:
                        continue
                    # 单元格关键词过滤：任意关键词匹配则保留
                    if cell_filter is not None and not any(
                        keyword in cell_text for keyword in cell_filter
                    ):
                        continue
                    # 存入对应任务分组
                    task_group[task_name].append(
                        {"阀点周期": week_name, "单元格值": cell_text}
                    )
            # ---------------------- 4. 转换输出格式 ----------------------
            result: List[Dict[str, Any]] = []
            for main_name, task_dict in main_data.items():
                item = {"项目": main_name}
                for task_name, task_list in task_dict.items():
                    # 将 [{"阀点周期": "2026.5.W3", "单元格值": "SOP 1/19"}] 转换为 {"SOP": ["2026.5.W3"]}
                    task_data: Dict[str, List[str]] = {}
                    for entry in task_list:
                        cell_value = entry["单元格值"]
                        week = entry["阀点周期"]
                        # 判断单元格值包含哪个关键词，归类到对应列表
                        if "SOP" in cell_value:
                            key = "SOP"
                        elif "OTA" in cell_value:
                            key = "OTA"
                        else:
                            key = cell_value
                        if key not in task_data:
                            task_data[key] = []
                        task_data[key].append(week)
                    item[task_name] = task_data
                result.append(item)
            # 排序
            result = ProjectPlanService.sort_data_by_week(result)

            # 提取未来三个月内的 整车发测中有任意SOP或 OTA 的数据
            now = datetime.now()
            # 手动计算三个月后的日期
            end_month = now.month + 3
            end_year = now.year
            if end_month > 12:
                end_year += end_month // 12
                end_month = end_month % 12
            three_months_later = now.replace(year=end_year, month=end_month)
            current_week = ProjectPlanService.date_to_week_str(now)
            end_week = ProjectPlanService.date_to_week_str(three_months_later)
            current_tuple = ProjectPlanService.week_str_to_comparable(current_week)
            end_tuple = ProjectPlanService.week_str_to_comparable(end_week)
            upcoming_vehicle_data: List[Dict[str, Any]] = []
            for item in result:
                vehicle_data = item.get("整车发测", {})
                if not vehicle_data:
                    continue

                sop_weeks = vehicle_data.get("SOP", [])
                ota_weeks = vehicle_data.get("OTA", [])

                # 判断是否有任意一条SOP或OTA在三个月范围内
                has_upcoming = any(
                    current_tuple
                    <= ProjectPlanService.week_str_to_comparable(w)
                    <= end_tuple
                    for w in sop_weeks + ota_weeks
                )

                if has_upcoming:
                    # 符合条件，返回该项目完整数据（包含所有任务）
                    upcoming_vehicle_data.append(item)

            return {
                "all_data": result,
                "upcoming_vehicle_tasks": upcoming_vehicle_data,
            }

        finally:
            # 安全关闭工作簿，释放文件句柄
            wb.close()

    @staticmethod
    async def async_parse_program_plan(
        file_path: str,
        task_filter: Optional[List[str]] = None,
        cell_filter: Optional[List[str]] = None,
    ) -> Dict[str, Any] | str:
        """异步包装解析函数，FastAPI接口调用专用"""
        abs_path = settings.UPLOAD_DIR / file_path
        if not os.path.exists(abs_path):
            abs_path = settings.UPLOAD_DIR / file_path
            if not os.path.exists(abs_path):
                return "文件不存在"
        print("abs_path", abs_path)
        # 2. 仅允许xlsx后缀
        if not abs_path.name.endswith(".xlsx"):
            return "仅支持.xlsx格式文件"
        # 3. 校验可读权限
        if not os.access(abs_path, os.R_OK):
            return "文件无读取权限"
        # 使用asyncio.to_thread将同步函数转换为异步函数，并在单独的线程中执行
        try:
            # 线程池执行同步CPU/IO解析逻辑
            excel_data = await asyncio.to_thread(
                ProjectPlanService.parse_program_plan,
                file_path=abs_path,
                task_filter=task_filter,
                cell_filter=cell_filter,
            )
            return excel_data
        except Exception as e:
            # 捕获Excel解析崩溃（Fill样式报错、损坏文件等）
            return f"文件解析失败：{str(e)}，请重试。"


plan_serve = ProjectPlanService()
