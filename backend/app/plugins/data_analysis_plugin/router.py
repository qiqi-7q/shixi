# import pandas as pd
#
# from fastapi import APIRouter
#
# router = APIRouter()
#
# """
# NAP统计函数
# 支持：
# - 线性KPI：传入原始里程/比率（浮点数或百分比字符串如"96.40%"）
# - 扣分型KPI：传入字典 {'percent': 95} 直接给百分制，或传入整数（表示默认事件次数），或字典{事件:次数}
# - 二分型KPI：传入0/1或布尔值
# """
#
#
# def linear_score(value, min_val, mid_val, max_val):
#     if value <= min_val:
#         return 0.0
#     if value >= max_val:
#         return 100.0
#     if value <= mid_val:
#         return 60.0 * (value - min_val) / (mid_val - min_val)
#     else:
#         return 60.0 + 40.0 * (value - mid_val) / (max_val - mid_val)
#
#
# def kpi_weighted_score(percent_score, full_score):
#     return percent_score / 100.0 * full_score
#
#
# class NAPStatistics:
#     def __init__(self):
#         # 1. 可靠性
#         self.reliability_kpis = {
#             "异常退出": {
#                 "full_score": 7.5,
#                 "type": "linear",
#                 "params": {"min": 400, "mid": 1500, "max": 4000},
#             },
#             "异常降级": {
#                 "full_score": 7.5,
#                 "type": "linear",
#                 "params": {"min": 200, "mid": 1000, "max": 2500},
#             },
#             "无法激活": {
#                 "full_score": 7.5,
#                 "type": "linear",
#                 "params": {"min": 2500, "mid": 6000, "max": 20000},
#             },
#             "系统异常": {
#                 "full_score": 7.5,
#                 "type": "linear",
#                 "params": {"min": 2500, "mid": 6000, "max": 20000},
#             },
#         }
#
#         # 2. 法规/安全性
#         self.safety_kpis = {
#             "碰撞风险": {
#                 "full_score": 9.0,
#                 "type": "linear",
#                 "params": {"min": 50, "mid": 100, "max": 1000},
#             },
#             "压实线": {
#                 "full_score": 9.0,
#                 "type": "linear",
#                 "params": {"min": 200, "mid": 500, "max": 4500},
#             },
#             "匝道红绿灯": {
#                 "full_score": 6.0,
#                 "type": "deduct",
#                 "deduct_rules": {"严重失效": 5, "一般失效": 2},
#                 "default_event": "严重失效",
#             },
#             "超速/低速": {
#                 "full_score": 6.0,
#                 "type": "linear",
#                 "params": {"min": 500, "mid": 800, "max": 3000},
#             },
#         }
#
#         # 3. 舒适性
#         self.comfort_kpis = {
#             "横向": {
#                 "full_score": 10.0,
#                 "type": "linear",
#                 "params": {"min": 50, "mid": 200, "max": 1000},
#             },
#             "纵向": {
#                 "full_score": 10.0,
#                 "type": "linear",
#                 "params": {"min": 50, "mid": 200, "max": 1000},
#             },
#         }
#
#         # 4. 可用性
#         self.availability_kpis = {
#             "变道成功率": {
#                 "full_score": 4.0,
#                 "type": "linear",
#                 "params": {"min": 0.80, "mid": 0.90, "max": 0.995},
#             },
#             "汇入成功率": {
#                 "full_score": 4.0,
#                 "type": "linear",
#                 "params": {"min": 0.80, "mid": 0.90, "max": 0.98},
#             },
#             "汇出成功率": {
#                 "full_score": 4.0,
#                 "type": "linear",
#                 "params": {"min": 0.80, "mid": 0.90, "max": 0.98},
#             },
#             "分合流": {
#                 "full_score": 2.0,
#                 "type": "linear",
#                 "params": {"min": 0.80, "mid": 0.90, "max": 0.98},
#             },
#             "特殊场景": {
#                 "full_score": 2.0,
#                 "type": "linear",
#                 "params": {"min": 0.60, "mid": 0.70, "max": 0.95},
#             },
#             "脱手监测": {
#                 "full_score": 1.0,
#                 "type": "deduct",
#                 "deduct_per_fault": 5,
#                 "default_event": "漏判误判",
#             },
#             "限速识别": {
#                 "full_score": 1.0,
#                 "type": "linear",
#                 "params": {"min": 0.90, "mid": 0.95, "max": 0.995},
#             },
#             "人机共驾": {"full_score": 1.0, "type": "binary"},
#             "微避障": {
#                 "full_score": 1.0,
#                 "type": "deduct",
#                 "deduct_rules": {"避障失败": 5, "危险行为": 3, "无回正压线": 2},
#                 "default_event": "避障失败",
#             },
#         }
#
#     def _normalize_value(self, value):
#         """将百分比字符串转换为浮点数，例如 '96.40%' -> 0.9640"""
#         if isinstance(value, str):
#             value = value.strip()
#             if value.endswith("%"):
#                 try:
#                     return float(value[:-1]) / 100.0
#                 except ValueError:
#                     pass
#             try:
#                 return float(value)
#             except ValueError:
#                 pass
#         return value
#
#     def _calc_percent_score(self, kpi_name, value, config):
#         value = self._normalize_value(value)
#         kpi_type = config["type"]
#
#         if isinstance(value, dict) and "percent" in value:
#             return max(0.0, min(100.0, float(value["percent"])))
#
#         if kpi_type == "linear":
#             params = config["params"]
#             return linear_score(value, params["min"], params["mid"], params["max"])
#
#         elif kpi_type == "deduct":
#             if isinstance(value, (int, float)):
#                 default_event = config.get("default_event")
#                 if default_event is not None:
#                     deduct_rules = config.get("deduct_rules", {})
#                     deduct_per = deduct_rules.get(default_event, 0)
#                     if deduct_per == 0:
#                         deduct_per = config.get("deduct_per_fault", 5)
#                     return max(0.0, 100.0 - value * deduct_per)
#                 else:
#                     deduct_per = config.get("deduct_per_fault", 5)
#                     return max(0.0, 100.0 - value * deduct_per)
#             if isinstance(value, dict):
#                 total_deduct = 0
#                 deduct_rules = config.get("deduct_rules", {})
#                 for event, cnt in value.items():
#                     if event in deduct_rules:
#                         total_deduct += cnt * deduct_rules[event]
#                 return max(0.0, 100.0 - total_deduct)
#             raise ValueError(f"{kpi_name} 的输入格式不正确")
#
#         elif kpi_type == "binary":
#             has_problem = value if isinstance(value, bool) else value > 0
#             return 0.0 if has_problem else 100.0
#
#         else:
#             raise ValueError(f"未知类型: {kpi_type}")
#
#     def _calc_module(self, kpis_dict, data):
#         total = 0.0
#         scores = {}
#         for kpi, config in kpis_dict.items():
#             if kpi not in data:
#                 continue
#             percent = self._calc_percent_score(kpi, data[kpi], config)
#             weighted = kpi_weighted_score(percent, config["full_score"])
#             scores[kpi] = weighted
#             total += weighted
#         return total, scores
#
#     def calculate(self, reliability_data, safety_data, comfort_data, availability_data):
#         result = {"modules": {}, "kpi_scores": {}, "total_score": 0.0}
#         for name, kpis, data in [
#             ("可靠性", self.reliability_kpis, reliability_data),
#             ("法规/安全性", self.safety_kpis, safety_data),
#             ("舒适性", self.comfort_kpis, comfort_data),
#             ("可用性", self.availability_kpis, availability_data),
#         ]:
#             score, details = self._calc_module(kpis, data)
#             result["modules"][name] = score
#             result["kpi_scores"].update(details)
#             result["total_score"] += score
#         return result
#
#
# def fmt(score):
#     return f"{round(score + 1e-9, 2):.2f}"
#
#
# def process_single_case(
#     nap, reliability_test, safety_test, comfort_test, availability_test
# ):
#     """处理单组测试数据并打印结果"""
#     result = nap.calculate(
#         reliability_test, safety_test, comfort_test, availability_test
#     )
#     print("=" * 60)
#     print("NAP统计结果")
#     print("=" * 60)
#     for module in ["可靠性", "法规/安全性", "舒适性", "可用性"]:
#         print(f"\n【{module}模块得分】: {fmt(result['modules'][module])} 分")
#         kpi_dict = getattr(
#             nap,
#             f"{'reliability' if module=='可靠性' else 'safety' if module=='法规/安全性' else 'comfort' if module=='舒适性' else 'availability'}_kpis",
#         )
#         for kpi in kpi_dict:
#             if kpi in result["kpi_scores"]:
#                 print(f"  {kpi}: {fmt(result['kpi_scores'][kpi])}")
#     print(f"\n最终总分: {fmt(result['total_score'])} 分")
#     return result
#
#
# def process_excel(nap, file_path, output_path=None):
#     """读取Excel文件并批量计算，结果保存到新Excel"""
#     df = pd.read_excel(file_path, dtype={"id": str})  # id保留字符串
#     results = []
#
#     for idx, row in df.iterrows():
#         # 提取各模块数据
#         reliability_data = {
#             "异常退出": row["异常退出"],
#             "异常降级": row["异常降级"],
#             "无法激活": row["无法激活"],
#             "系统异常": row["系统异常"],
#         }
#         safety_data = {
#             "碰撞风险": row["碰撞风险"],
#             "压实线": row["压实线"],
#             "匝道红绿灯": row["匝道红绿灯"],
#             "超速/低速": row["超速/低速"],
#         }
#         comfort_data = {
#             "横向": row["横向"],
#             "纵向": row["纵向"],
#         }
#         availability_data = {
#             "变道成功率": row["变道成功率"],
#             "汇入成功率": row["汇入成功率"],
#             "汇出成功率": row["汇出成功率"],
#             "分合流": row["分合流"],
#             "特殊场景": row["特殊场景"],
#             "脱手监测": row["脱手监测"],
#             "限速识别": row["限速识别"],
#             "人机共驾": row["人机共驾"],
#             "微避障": row["微避障"],
#         }
#
#         result = nap.calculate(
#             reliability_data, safety_data, comfort_data, availability_data
#         )
#
#         # 构造结果记录
#         record = {
#             "id": row["id"],
#             "可靠性模块得分": result["modules"]["可靠性"],
#             "法规安全性模块得分": result["modules"]["法规/安全性"],
#             "舒适性模块得分": result["modules"]["舒适性"],
#             "可用性模块得分": result["modules"]["可用性"],
#             "最终总分": result["total_score"],
#         }
#         # 加入每个KPI的加权得分
#         for kpi, score in result["kpi_scores"].items():
#             record[kpi + "_加权得分"] = score
#         results.append(record)
#
#     # 保存结果
#     result_df = pd.DataFrame(results)
#     if output_path is None:
#         output_path = file_path.replace(".xlsx", "_结果.xlsx")
#     result_df.to_excel(output_path, index=False)
#     print(f"批量计算完成！共处理 {len(results)} 个任务，结果已保存至：{output_path}")
#
#     # 控制台打印概要
#     print("\n任务得分预览：")
#     print(
#         result_df[
#             [
#                 "id",
#                 "可靠性模块得分",
#                 "法规安全性模块得分",
#                 "舒适性模块得分",
#                 "可用性模块得分",
#                 "最终总分",
#             ]
#         ]
#         .head(3)
#         .to_string(index=False)
#     )
#     return results
#
#
# if __name__ == "__main__":
#     import os
#
#     nap = NAPStatistics()
#     # 获取当前脚本所在目录
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     excel_path = os.path.join(script_dir, "test_data.xlsx")
#
#     # 判断文件是否存在
#     if os.path.exists(excel_path):
#         print(f"检测到Excel文件：{excel_path}，将批量读取并计算所有测试任务。")
#         process_excel(nap, excel_path)
#     else:
#         print("未检测到Excel文件，使用内置写死数据运行单次计算。")
#         # 写死测试数据
#         reliability_test = {
#             "异常退出": 1500,
#             "异常降级": 500,
#             "无法激活": 20000,
#             "系统异常": 20000,
#         }
#         safety_test = {
#             "碰撞风险": 250,
#             "压实线": 350,
#             "匝道红绿灯": 1,
#             "超速/低速": 3000,
#         }
#         comfort_test = {
#             "横向": 60,
#             "纵向": 120,
#         }
#         availability_test = {
#             "变道成功率": "96.40%",
#             "汇入成功率": "100%",
#             "汇出成功率": "96.72%",
#             "分合流": "93.75%",
#             "特殊场景": "100%",
#             "脱手监测": 0,
#             "限速识别": "100%",
#             "人机共驾": 0,
#             "微避障": 2,
#         }
#         process_single_case(
#             nap, reliability_test, safety_test, comfort_test, availability_test
#         )
