from typing import Optional

from app.plugins.test_miles_plugin.models import TestMiles
from fastapi import Depends, Query
from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.plugins.data_analysis_plugin.models import KpiItem, KpiMain, KpiModule
from app.plugins.test_record_plugin.models import TestRecord
from app.plugins.vehicle_plugin.models import Vehicle

# ====================== 评分指标======================
# 1. 可靠性
EXIT_CFG = {
    "full_score": 7.5,
    "score_proportion": 0.25,
    "type": "linear",
    "params": {"min": 400, "mid": 1500, "max": 4000},
}
DOWNGRADE_CFG = {
    "full_score": 7.5,
    "score_proportion": 0.25,
    "type": "linear",
    "params": {"min": 200, "mid": 1000, "max": 2500},
}
UNACTIVATE_CFG = {
    "full_score": 7.5,
    "score_proportion": 0.25,
    "type": "linear",
    "params": {"min": 2500, "mid": 6000, "max": 20000},
}
EXCEPTION_CFG = {
    "full_score": 7.5,
    "score_proportion": 0.25,
    "type": "linear",
    "params": {"min": 2500, "mid": 6000, "max": 20000},
}

# 2. 法规/安全性
COLLISION_CFG = {
    "full_score": 9.0,
    "score_proportion": 0.3,
    "type": "linear",
    "params": {"min": 50, "mid": 100, "max": 1000},
}
CRASH_CFG = {
    "full_score": 9.0,
    "score_proportion": 0.3,
    "type": "linear",
    "params": {"min": 200, "mid": 500, "max": 4500},
}
RED_GREEN_CFG = {
    "full_score": 6.0,
    "score_proportion": 0.2,
    "type": "deduct",
    "deduct_rules": {"severe": 5, "general": 2},
    "default_event": "severe",
}
OVER_LOW_CFG = {
    "full_score": 6.0,
    "score_proportion": 0.2,
    "type": "linear",
    "params": {"min": 500, "mid": 800, "max": 3000},
}

# 3. 舒适性
LATERAL_CFG = {
    "full_score": 10.0,
    "score_proportion": 0.5,
    "type": "linear",
    "params": {"min": 50, "mid": 200, "max": 1000},
}
VERTICAL_CFG = {
    "full_score": 10.0,
    "score_proportion": 0.5,
    "type": "linear",
    "params": {"min": 50, "mid": 200, "max": 1000},
}

# 4. 可用性
CHANGELANE_CFG = {
    "full_score": 4.0,
    "score_proportion": 0.2,
    "type": "linear",
    "params": {"min": 0.80, "mid": 0.90, "max": 0.995},
}
UNAVA_CHANGELANE_CFG = {
    "full_score": 4.0,
    "score_proportion": 0.2,
    "type": "deduct",
    "deduct_rules": {"fail": 5},
    "default_event": "fail",
}
INFLOW_CFG = {
    "full_score": 4.0,
    "score_proportion": 0.2,
    "type": "linear",
    "params": {"min": 0.80, "mid": 0.90, "max": 0.98},
}
OUTFLOW_CFG = {
    "full_score": 4.0,
    "score_proportion": 0.2,
    "type": "linear",
    "params": {"min": 0.80, "mid": 0.90, "max": 0.98},
}
DIVERGE_CONVERGE_CFG = {
    "full_score": 2.0,
    "score_proportion": 0.1,
    "type": "linear",
    "params": {"min": 0.80, "mid": 0.90, "max": 0.98},
}
SPECIAL_CFG = {
    "full_score": 2.0,
    "score_proportion": 0.1,
    "type": "linear",
    "params": {"min": 0.60, "mid": 0.70, "max": 0.95},
}
DROPPED_CFG = {
    "full_score": 1.0,
    "score_proportion": 0.05,
    "type": "deduct",
    "deduct_per_fault": 5,
    "default_event": "漏判误判",
}
RECOG_CFG = {
    "full_score": 1.0,
    "score_proportion": 0.05,
    "type": "linear",
    "params": {"min": 0.90, "mid": 0.95, "max": 0.995},
}
HUMAN_MACHINE_CFG = {"full_score": 1.0, "score_proportion": 0.05, "type": "binary"}
MICRO_OA_CFG = {
    "full_score": 1.0,
    "score_proportion": 0.05,
    "type": "deduct",
    "deduct_rules": {"fail": 5, "brake_direction": 3, "no_return_line": 2},
    "default_event": "fail",
}

# KPI文本标签映射
KPI_LABEL_MAP = {
    "异常退出": "EXIT",
    "异常降级": "DOWNGRADE",
    "无法激活": "UNACTIVATE",
    "系统异常": "EXCEPTION",
    "碰撞风险": "COLLISION",
    "压实线": "CRASH",
    "匝道红绿灯严重失效（导致闯红灯）": "RED_GREEN_SEVERE",
    "匝道红绿灯一般失效（错误减速/加速）": "RED_GREEN_GENERAL",
    "超速/低速": "OVER_LOW",
    "横向": "LATERAL",
    "纵向": "VERTICAL",
    "变道成功": "CHANGELANE_S",
    "变道失败": "CHANGELANE_F",
    "无效变道（如无必要的反复变道）": "UNAVA_CHANGELANE",
    "汇入成功": "INFLOW_S",
    "汇入失败": "INFLOW_F",
    "汇出成功": "OUTFLOW_S",
    "汇出失败": "OUTFLOW_F",
    "分合流成功": "DIVERGE_CONVERGE_S",
    "分合流失败": "DIVERGE_CONVERGE_F",
    "特殊场景通过成功": "SPECIAL_S",
    "特殊场景通过失败": "SPECIAL_F",
    "脱手监测": "DROPPED",
    "限速识别成功": "RECOG_S",
    "限速识别失败": "RECOG_F",
    "人机共驾接管冲突": "H_M_C",
    "人机共驾失控车辆失控风险": "H_M_U",
    "微避障失败": "MICRO_OA_FAIL",
    "微避障急刹/猛打方向": "MICRO_OA_B",
    "微避障无回正、压线": "MICRO_OA_R",
}


class DataAnalysis:
    # ====================== 通用计算======================
    @staticmethod
    def linear_score(value, min_val, mid_val, max_val) -> float:
        """线性分段原始分计算"""
        if value <= min_val:
            return 0.0
        if value >= max_val:
            return 100.0
        if value <= mid_val:
            return 60.0 / (mid_val - min_val) * (value - min_val)
        else:
            return 60.0 + 40.0 / (max_val - mid_val) * (value - mid_val)

    @staticmethod
    def weighted_score(primitive_score: float, full_score: float) -> float:
        """计算加权得分"""
        return primitive_score * full_score / 100.0

    @staticmethod
    def success_rate(sc_count: float, full_count: float) -> float:
        """计算成功率"""
        return sc_count / full_count if full_count != 0 else 0.0

    @staticmethod
    def format_score(score: float) -> str:
        """分值格式化，保留2位小数，实现四舍五入"""
        return f"{round(score + 1e-9, 2):.2f}"

    # ====================== KPI项计算======================
    @staticmethod
    def calc_linear_kpi(total_val: float, cfg: dict) -> tuple[float, float]:
        """
        通用线性指标计算
        :param total_val: 统计值（里程/成功率等）
        :param cfg: 指标配置字典
        :return: (原始分, 加权分)
        """
        params = cfg["params"]
        raw = DataAnalysis.linear_score(
            total_val, params["min"], params["mid"], params["max"]
        )
        weight = DataAnalysis.weighted_score(raw, cfg["full_score"])
        print(f"原始分：{raw}, 加权分：{weight}")
        return raw, weight

    @staticmethod
    def calc_changelane_kpi(
        total_val: float, times: int, cfg: dict, uncfg: dict
    ) -> tuple[float, float]:
        """
        变道成功率指标计算
        :param total_val: 统计值（成功率等）
        :param cfg: 指标配置字典
        :param times: 失败次数
        :param uncfg: 不成功指标配置字典
        :return: (原始分, 加权分)
        """
        params = cfg["params"]
        unparams = uncfg["deduct_rules"]
        need_deduct = times * unparams["fail"]
        raw = max(
            0.0,
            DataAnalysis.linear_score(
                total_val, params["min"], params["mid"], params["max"]
            )
            - need_deduct,
        )
        weight = DataAnalysis.weighted_score(raw, cfg["full_score"])
        return raw, weight

    @staticmethod
    def calc_deduct_kpi_base(total_deduct: float) -> float:
        """扣分类指标基础原始分"""
        return max(0.0, 100.0 - total_deduct)

    @staticmethod
    def calc_red_green_kpi(
        severe_times: int, general_times: int
    ) -> tuple[float, float]:
        """匝道红绿灯扣分计算"""
        deduct = (
            severe_times * RED_GREEN_CFG["deduct_rules"]["severe"]
            + general_times * RED_GREEN_CFG["deduct_rules"]["general"]
        )
        raw = max(0.0, DataAnalysis.calc_deduct_kpi_base(deduct))
        weight = DataAnalysis.weighted_score(raw, RED_GREEN_CFG["full_score"])
        return raw, weight

    @staticmethod
    def calc_dropped_kpi(DROPPED: int) -> tuple[float, float]:
        """脱手监测扣分计算"""
        deduct = DROPPED * DROPPED_CFG["deduct_per_fault"]
        raw = max(0.0, DataAnalysis.calc_deduct_kpi_base(deduct))
        weight = DataAnalysis.weighted_score(raw, DROPPED_CFG["full_score"])
        return raw, weight

    @staticmethod
    def calc_human_machine_kpi(H_M_C: int, H_M_U: int) -> tuple[float, float]:
        """人机共驾二值型计算"""
        raw = 0.0 if (H_M_C + H_M_U) > 0 else 100.0
        weight = DataAnalysis.weighted_score(raw, HUMAN_MACHINE_CFG["full_score"])
        return raw, weight

    @staticmethod
    def calc_micro_oa_kpi(
        MICRO_OA_FAIL: int, MICRO_OA_B: int, MICRO_OA_R: int
    ) -> tuple[float, float]:
        """微避障多维度扣分计算"""
        rule = MICRO_OA_CFG["deduct_rules"]
        deduct = (
            MICRO_OA_FAIL * rule["fail"]
            + MICRO_OA_B * rule["brake_direction"]
            + MICRO_OA_R * rule["no_return_line"]
        )
        raw = max(0.0, DataAnalysis.calc_deduct_kpi_base(deduct))
        weight = DataAnalysis.weighted_score(raw, MICRO_OA_CFG["full_score"])
        return raw, weight

    # ====================== 统计所有KPI次数======================
    @staticmethod
    def kpi_times_count(total_test_miles: float, records: list) -> dict:
        """
        仅遍历一次列表，统计所有KPI出现次数
        :param total_test_miles: 总测试里程
        :param records: test_records 列表
        :return: 包含所有计数字段的字典
        """
        stat_fields = KPI_LABEL_MAP.values()
        # 初始化所有计数为0
        stat_data = {field: 0 for field in stat_fields}
        # 一次遍历完成全量统计
        for rec in records:
            label = rec.kpi_type
            label_c = str(label).split(".")[-1]
            if label_c in stat_fields:
                stat_data[label_c] += 1

        # 计算每个KPI的MPI 总里程/次数
        for field in stat_fields:
            ratio_key = f"{field}_ratio"
            count = stat_data[field]
            if count > 0:
                stat_data[ratio_key] = total_test_miles / count
            else:
                stat_data[ratio_key] = 0.0
        return stat_data

    # ====================== 数据查询 + 全量计算 ======================
    @staticmethod
    async def need_analysis_data(
        db: AsyncSession,
        project: str,
        model: str,
        version: str,
        funcMode: str,
    ) -> dict | str | list:
        """
        主分析入口：查询数据 + 计算四大模块总分
        """
        # 入参校验
        if not project:
            return "项目不能为空"
        if not model:
            return "车型不能为空"
        if not version:
            return "版本不能为空"
        if not funcMode:
            return "功能不能为空"

        # 查询测试记录
        test_rec = await db.execute(
            select(TestRecord).where(
                TestRecord.project == project,
                TestRecord.car_type == model,
                TestRecord.software_version == version,
                TestRecord.function_mode == funcMode,
            )
        )
        test_records = list(test_rec.scalars().all())
        if not test_records:
            return "无测试数据"

        # 查询该版本下的所有VIN码（从测试记录表获取，不区分车型）
        test_record_vin_stmt = (
            select(TestRecord.vin_code)
            .distinct()
            .where(
                TestRecord.project == project,
                TestRecord.software_version == version,
                TestRecord.function_mode == funcMode,
            )
        )
        test_record_vin_result = await db.execute(test_record_vin_stmt)
        vehicle_vins = [row[0] for row in test_record_vin_result.all()]

        if not vehicle_vins:
            return "该版本暂无车辆数据"

        # 查询里程数据（按版本对应的VIN码过滤，不区分车型）
        test_miles = await db.execute(
            select(TestMiles).where(
                TestMiles.is_kpi == True,
                TestMiles.project == project,
                TestMiles.test_version == version,
                TestMiles.test_function == funcMode,
                TestMiles.vin_code.in_(vehicle_vins),
            )
        )
        test_miles_records = list(test_miles.scalars().all())

        if not test_miles_records:
            return "无测试里程数据"

        # 基础统计值
        total_test_miles = sum(rec.mileage for rec in test_miles_records)
        print(f"总测试里程:", total_test_miles)

        # 统计主表部分数据
        kpiMileage = total_test_miles

        # 统计所有KPI项出现次数
        kpi_stat = DataAnalysis.kpi_times_count(total_test_miles, test_records)
        print("KPI出现次数:", kpi_stat)

        # {     次数
        #     "EXIT": 2,
        #       MPI（测试结果）
        #     "MICRO_OA_R": 0.0}

        # 计算变道成功率、汇入成功率、汇出成功率、分合流、特殊场景、限速识别
        avaliable_change = kpi_stat["CHANGELANE_S"] + kpi_stat["CHANGELANE_F"]
        change_lane_success_rate = DataAnalysis.success_rate(
            kpi_stat["CHANGELANE_S"], avaliable_change
        )
        print("变道成功率:", change_lane_success_rate)
        total_inflow = kpi_stat["INFLOW_S"] + kpi_stat["INFLOW_F"]
        inflow_success_rate = DataAnalysis.success_rate(
            kpi_stat["INFLOW_S"], total_inflow
        )
        print("汇入成功率:", inflow_success_rate)
        total_outflow = kpi_stat["OUTFLOW_S"] + kpi_stat["OUTFLOW_F"]
        outflow_success_rate = DataAnalysis.success_rate(
            kpi_stat["OUTFLOW_S"], total_outflow
        )
        print("汇出成功率:", outflow_success_rate)
        total_diverge_converge = (
            kpi_stat["DIVERGE_CONVERGE_S"] + kpi_stat["DIVERGE_CONVERGE_F"]
        )
        diverge_converge_rate = DataAnalysis.success_rate(
            kpi_stat["DIVERGE_CONVERGE_S"], total_diverge_converge
        )
        print("分合流成功率:", diverge_converge_rate)
        total_special = kpi_stat["SPECIAL_S"] + kpi_stat["SPECIAL_F"]
        special_rate = DataAnalysis.success_rate(kpi_stat["SPECIAL_S"], total_special)
        print("特殊场景成功率:", special_rate)
        total_recog = kpi_stat["RECOG_S"] + kpi_stat["RECOG_F"]
        recog_rate = DataAnalysis.success_rate(kpi_stat["RECOG_S"], total_recog)
        print("限速识别成功率:", recog_rate)

        # 计算【可靠性】模块
        exit_r, exit_w = DataAnalysis.calc_linear_kpi(kpi_stat["EXIT_ratio"], EXIT_CFG)
        downgrade_r, downgrade_w = DataAnalysis.calc_linear_kpi(
            kpi_stat["DOWNGRADE_ratio"], DOWNGRADE_CFG
        )
        unactivate_r, unactivate_w = DataAnalysis.calc_linear_kpi(
            kpi_stat["UNACTIVATE_ratio"], UNACTIVATE_CFG
        )
        exception_r, exception_w = DataAnalysis.calc_linear_kpi(
            kpi_stat["EXCEPTION_ratio"], EXCEPTION_CFG
        )
        reliability_s = exit_w + downgrade_w + unactivate_w + exception_w

        # 计算【法规/安全性】模块
        collision_r, collision_w = DataAnalysis.calc_linear_kpi(
            kpi_stat["COLLISION_ratio"], COLLISION_CFG
        )
        crash_r, crash_w = DataAnalysis.calc_linear_kpi(
            kpi_stat["CRASH_ratio"], CRASH_CFG
        )
        red_green_r, red_green_w = DataAnalysis.calc_red_green_kpi(
            kpi_stat["RED_GREEN_SEVERE"], kpi_stat["RED_GREEN_GENERAL"]
        )
        over_low_r, over_low_w = DataAnalysis.calc_linear_kpi(
            kpi_stat["OVER_LOW_ratio"], OVER_LOW_CFG
        )
        regulationsSafety_s = collision_w + crash_w + red_green_w + over_low_w

        # 计算【舒适性】模块
        lateral_r, lateral_w = DataAnalysis.calc_linear_kpi(
            kpi_stat["LATERAL_ratio"], LATERAL_CFG
        )
        vertical_r, vertical_w = DataAnalysis.calc_linear_kpi(
            kpi_stat["VERTICAL_ratio"], VERTICAL_CFG
        )
        comfort_s = lateral_w + vertical_w

        # 计算【可用性】模块
        changelane_r, cl_w = DataAnalysis.calc_changelane_kpi(
            change_lane_success_rate,
            kpi_stat["UNAVA_CHANGELANE"],
            CHANGELANE_CFG,
            UNAVA_CHANGELANE_CFG,
        )
        inflow_r, inflow_w = DataAnalysis.calc_linear_kpi(
            inflow_success_rate, INFLOW_CFG
        )
        outflow_r, outflow_w = DataAnalysis.calc_linear_kpi(
            outflow_success_rate, OUTFLOW_CFG
        )
        split_r, split_w = DataAnalysis.calc_linear_kpi(
            diverge_converge_rate, DIVERGE_CONVERGE_CFG
        )
        special_r, special_w = DataAnalysis.calc_linear_kpi(special_rate, SPECIAL_CFG)
        recog_r, recog_w = DataAnalysis.calc_linear_kpi(recog_rate, RECOG_CFG)
        dropped_r, dropped_w = DataAnalysis.calc_dropped_kpi(kpi_stat["DROPPED"])
        hm_r, hm_w = DataAnalysis.calc_human_machine_kpi(
            kpi_stat["H_M_C"], kpi_stat["H_M_U"]
        )
        mo_r, mo_w = DataAnalysis.calc_micro_oa_kpi(
            kpi_stat["MICRO_OA_FAIL"], kpi_stat["MICRO_OA_B"], kpi_stat["MICRO_OA_R"]
        )
        usability_s = (
            cl_w
            + inflow_w
            + outflow_w
            + split_w
            + special_w
            + recog_w
            + dropped_w
            + hm_w
            + mo_w
        )

        # 计算总分、保留两位小数总分
        total_s = reliability_s + regulationsSafety_s + comfort_s + usability_s
        total_s_2 = DataAnalysis.format_score(total_s)

        return {
            "mainData": {"kpiMileage": kpiMileage},
            "kpis": (
                "exit",
                "downgrade",
                "unactivate",
                "exception",
                "collision",
                "crash",
                "red_green",
                "over_low",
                "lateral",
                "vertical",
                "change_lane_s",
                "inflow_s",
                "outflow_s",
                "diverge_converge_s",
                "special_s",
                "dropped_s",
                "recog_s",
                "hm_s",
                "mo_s",
            ),
            "counts": {
                "exit": kpi_stat["EXIT"],
                "downgrade": kpi_stat["DOWNGRADE"],
                "unactivate": kpi_stat["UNACTIVATE"],
                "exception": kpi_stat["EXCEPTION"],
                "collision": kpi_stat["COLLISION"],
                "crash": kpi_stat["CRASH"],
                "red_green": kpi_stat["RED_GREEN_SEVERE"]
                + kpi_stat["RED_GREEN_GENERAL"],
                "over_low": kpi_stat["OVER_LOW"],
                "lateral": kpi_stat["LATERAL"],
                "vertical": kpi_stat["VERTICAL"],
                "change_lane_s": avaliable_change + kpi_stat["UNAVA_CHANGELANE"],
                "inflow_s": total_inflow,
                "outflow_s": total_outflow,
                "diverge_converge_s": total_diverge_converge,
                "special_s": total_special,
                "dropped_s": kpi_stat["DROPPED"],
                "recog_s": total_recog,
                "hm_s": kpi_stat["H_M_C"] + kpi_stat["H_M_U"],
                "mo_s": kpi_stat["MICRO_OA_FAIL"]
                + kpi_stat["MICRO_OA_B"]
                + kpi_stat["MICRO_OA_R"],
            },
            "MPI": {
                "exit": kpi_stat["EXIT_ratio"],
                "downgrade": kpi_stat["DOWNGRADE_ratio"],
                "unactivate": kpi_stat["UNACTIVATE_ratio"],
                "exception": kpi_stat["EXCEPTION_ratio"],
                "collision": kpi_stat["COLLISION_ratio"],
                "crash": kpi_stat["CRASH_ratio"],
                "red_green": kpi_stat["RED_GREEN_SEVERE"]
                + kpi_stat["RED_GREEN_GENERAL"],
                "over_low": kpi_stat["OVER_LOW_ratio"],
                "lateral": kpi_stat["LATERAL_ratio"],
                "vertical": kpi_stat["VERTICAL_ratio"],
                "change_lane_s": change_lane_success_rate,
                "inflow_s": inflow_success_rate,
                "outflow_s": outflow_success_rate,
                "diverge_converge_s": diverge_converge_rate,
                "special_s": special_rate,
                "dropped_s": kpi_stat["DROPPED_ratio"],
                "recog_s": recog_rate,
                "hm_s": kpi_stat["H_M_C"] + kpi_stat["H_M_U"],
                "mo_s": kpi_stat["MICRO_OA_FAIL"]
                + kpi_stat["MICRO_OA_B"]
                + kpi_stat["MICRO_OA_R"],
            },
            "score_r": {
                "exit": exit_r,
                "downgrade": downgrade_r,
                "unactivate": unactivate_r,
                "exception": exception_r,
                "collision": collision_r,
                "crash": crash_r,
                "red_green": red_green_r,
                "over_low": over_low_r,
                "lateral": lateral_r,
                "vertical": vertical_r,
                "change_lane_s": changelane_r,
                "inflow_s": inflow_r,
                "outflow_s": outflow_r,
                "diverge_converge_s": split_r,
                "special_s": special_r,
                "dropped_s": dropped_r,
                "recog_s": recog_r,
                "hm_s": hm_r,
                "mo_s": mo_r,
            },
            "score_w": {
                "exit": exit_w,
                "downgrade": downgrade_w,
                "unactivate": unactivate_w,
                "exception": exception_w,
                "collision": collision_w,
                "crash": crash_w,
                "red_green": red_green_w,
                "over_low": over_low_w,
                "lateral": lateral_w,
                "vertical": vertical_w,
                "change_lane_s": cl_w,
                "inflow_s": inflow_w,
                "outflow_s": outflow_w,
                "diverge_converge_s": split_w,
                "special_s": special_w,
                "dropped_s": dropped_w,
                "recog_s": recog_w,
                "hm_s": hm_w,
                "mo_s": mo_w,
            },
            "module_s": {
                "reliability_s": reliability_s,
                "regulationsSafety_s": regulationsSafety_s,
                "comfort_s": comfort_s,
                "usability_s": usability_s,
            },
            "total": {"total_s": total_s, "total_s_2": total_s_2},
        }

    # ====================== 主入口：存数据库 ======================
    @staticmethod
    async def save_to_db(
        db: AsyncSession, project: str, model: str, version: str, funcMode: str
    ):
        try:
            stmt = select(KpiMain).where(
                KpiMain.project == project,
                KpiMain.carModel == model,
                KpiMain.version == version,
                KpiMain.funcMode == funcMode,
            )
            exists = await db.scalar(stmt)
            if exists:
                # 覆盖更新：先删除关联数据
                module_stmt = select(KpiModule).where(KpiModule.main_id == exists.id)
                module_exists = await db.scalar(module_stmt)
                if module_exists:
                    # 删除 kpi_item 关联数据
                    await db.execute(
                        delete(KpiItem).where(KpiItem.module_id == module_exists.id)
                    )
                    # 删除 kpi_module 数据
                    await db.delete(module_exists)
                # 删除 kpi_main 数据
                await db.delete(exists)
                await db.flush()

            save_data = await DataAnalysis.need_analysis_data(
                db=db, project=project, model=model, version=version, funcMode=funcMode
            )
            if isinstance(save_data, str):
                return save_data

            mainData = save_data["mainData"]
            kpis = save_data["kpis"]
            counts = save_data["counts"]
            MPIData = save_data["MPI"]
            score_r = save_data["score_r"]
            score_w = save_data["score_w"]
            module_s = save_data["module_s"]
            total = save_data["total"]

            if not (
                len(kpis) == len(counts) == len(MPIData) == len(score_r) == len(score_w)
            ):
                return "KPI各组数据长度不匹配，禁止入库"

            main_data = KpiMain(
                project=project,
                carModel=model,
                version=version,
                funcMode=funcMode,
                kpiMileage=mainData["kpiMileage"],
                totalScore=total["total_s_2"],
            )
            db.add(main_data)
            await db.flush()

            module_data = KpiModule(
                main_id=main_data.id,
                reliability=module_s["reliability_s"],
                regulationsSafety=module_s["regulationsSafety_s"],
                comfort=module_s["comfort_s"],
                usability=module_s["usability_s"],
            )
            db.add(module_data)
            await db.flush()

            enter_list = []
            for kpi in kpis:
                if (
                    kpi not in counts
                    or kpi not in MPIData
                    or kpi not in score_r
                    or kpi not in score_w
                ):
                    return f"数据中缺少{kpi}，禁止入库"

                entity = KpiItem(
                    module_id=module_data.id,
                    KPIType=kpi,
                    KPICount=counts[kpi],
                    MPI=MPIData[kpi],
                    RawScore=score_r[kpi],
                    KPIScore=score_w[kpi],
                )
                enter_list.append(entity)

            db.add_all(enter_list)
            await db.commit()

            return "success"

        except Exception as e:
            await db.rollback()
            return f"保存数据失败，错误信息: {str(e)}"

    # ====================== 查询符合条件的所有的分析数据 ======================
    @staticmethod
    async def get_analysis_datas(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=1000),
        db: AsyncSession = Depends(get_db),
        project: Optional[str] = None,
        carModel: Optional[str] = None,
        version: Optional[str] = None,
        funcMode: Optional[str] = None,
    ):
        query_cons = [
            KpiMain.is_del == False,
        ]
        if project:
            query_cons.append(KpiMain.project.icontains(project))
        if carModel:
            query_cons.append(KpiMain.carModel.icontains(carModel))
        if version:
            query_cons.append(KpiMain.version == version)
        if funcMode:
            query_cons.append(KpiMain.funcMode == funcMode)

        # 2. 先查符合条件的总条数（不带分页）
        count_stmt = select(func.count(KpiMain.id)).where(*query_cons)
        total = await db.scalar(count_stmt) or 0

        stmt = (
            select(KpiMain)
            .where(*query_cons)
            .order_by(KpiMain.id.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        data_list = list(result.scalars().all())
        return data_list, total

    # ====================== 查询单条分析数据 ======================
    @staticmethod
    async def get_analysis_info(db: AsyncSession, analysis_id: int):
        if not analysis_id:
            return "分析数据ID不能为空"
        stmt = await db.get(KpiMain, analysis_id)
        if not stmt:
            return "分析数据不存在"
        # 从KpiModule表中获取main_id=analysis_id的模块数据
        module_data = await db.execute(
            select(KpiModule).where(KpiModule.main_id == analysis_id)
        )
        module_data = module_data.scalars().first()
        # 从KpiItem表中获取module_id=module_data.id的KPI明细项数据
        item_data = await db.execute(
            select(KpiItem).where(KpiItem.module_id == module_data.id)
        )
        item_data = item_data.scalars().all()
        stmtdata = {
            "project": stmt.project,
            "carModel": stmt.carModel,
            "version": stmt.version,
            "funcMode": stmt.funcMode,
            "kpiMileage": stmt.kpiMileage,
            "totalScore": stmt.totalScore,
            "reliability": module_data.reliability,
            "regulationsSafety": module_data.regulationsSafety,
            "comfort": module_data.comfort,
            "usability": module_data.usability,
        }
        for item in item_data:
            stmtdata[item.KPIType] = {
                "KPICount": item.KPICount,
                "MPI": item.MPI,
                "RawScore": item.RawScore,
                "KPIScore": item.KPIScore,
            }
        return stmtdata

    # ====================== 对比分析数据 ======================
    @staticmethod
    async def compare_analysis_data(
        db: AsyncSession, analysis_id1: int, analysis_id2: int
    ):
        if not analysis_id1 or not analysis_id2:
            return "必须提供两个分析数据ID"
        if analysis_id1 == analysis_id2:
            return "两个分析数据ID不能相同"
        analysis_info1 = await dataAnalysis.get_analysis_info(db, analysis_id1)
        analysis_info2 = await dataAnalysis.get_analysis_info(db, analysis_id2)
        if isinstance(analysis_info1, str) or isinstance(analysis_info2, str):
            return "统计数据不存在，请检查ID是否正确"

        return [analysis_info1, analysis_info2]

    # ====================== 手动更新成功率指标 ======================
    @staticmethod
    async def update_success_rate(
        db: AsyncSession,
        project: str,
        model: str,
        version: str,
        funcMode: str,
        change_lane_success_rate: float,
        inflow_success_rate: float,
        outflow_success_rate: float,
        diverge_converge_rate: float,
        special_rate: float,
        recog_rate: float,
    ):
        """
        手动更新成功率指标并重新计算KPI得分
        :param db: 数据库会话
        :param project: 项目
        :param model: 车型
        :param version: 版本
        :param funcMode: 功能模式
        :param change_lane_success_rate: 变道成功率(0-100)
        :param inflow_success_rate: 汇入成功率(0-100)
        :param outflow_success_rate: 汇出成功率(0-100)
        :param diverge_converge_rate: 分合流成功率(0-100)
        :param special_rate: 特殊场景成功率(0-100)
        :param recog_rate: 限速识别成功率(0-100)
        """
        try:
            # 入参校验
            if not project or not model or not version or not funcMode:
                return "项目、车型、版本、功能不能为空"

            # 检查是否存在对应的KPI主记录
            main_stmt = select(KpiMain).where(
                KpiMain.project == project,
                KpiMain.carModel == model,
                KpiMain.version == version,
                KpiMain.funcMode == funcMode,
            )
            main_exists = await db.scalar(main_stmt)
            if not main_exists:
                return "未找到对应的KPI分析记录"

            # 查询模块记录
            module_stmt = select(KpiModule).where(KpiModule.main_id == main_exists.id)
            module_exists = await db.scalar(module_stmt)
            if not module_exists:
                return "未找到对应的KPI模块记录"

            # 查询测试记录获取其他KPI统计
            test_rec = await db.execute(
                select(TestRecord).where(
                    TestRecord.project == project,
                    TestRecord.car_type == model,
                    TestRecord.software_version == version,
                    TestRecord.function_mode == funcMode,
                )
            )
            test_records = list(test_rec.scalars().all())

            # 查询里程数据（按版本对应的VIN码过滤，不区分车型）
            test_record_vin_stmt = (
                select(TestRecord.vin_code)
                .distinct()
                .where(
                    TestRecord.project == project,
                    TestRecord.software_version == version,
                    TestRecord.function_mode == funcMode,
                )
            )
            test_record_vin_result = await db.execute(test_record_vin_stmt)
            vehicle_vins = [row[0] for row in test_record_vin_result.all()]

            test_miles = await db.execute(
                select(TestMiles).where(
                    TestMiles.is_kpi == True,
                    TestMiles.project == project,
                    TestMiles.test_version == version,
                    TestMiles.test_function == funcMode,
                    TestMiles.vin_code.in_(vehicle_vins) if vehicle_vins else True,
                )
            )
            test_miles_records = list(test_miles.scalars().all())
            total_test_miles = sum(rec.mileage for rec in test_miles_records)

            # 统计KPI次数
            kpi_stat = DataAnalysis.kpi_times_count(total_test_miles, test_records)

            # 使用手动输入的成功率（转换为小数）
            change_lane_success_rate = change_lane_success_rate / 100.0
            inflow_success_rate = inflow_success_rate / 100.0
            outflow_success_rate = outflow_success_rate / 100.0
            diverge_converge_rate = diverge_converge_rate / 100.0
            special_rate = special_rate / 100.0
            recog_rate = recog_rate / 100.0

            # 计算【可靠性】模块（不变）
            exit_r, exit_w = DataAnalysis.calc_linear_kpi(
                kpi_stat["EXIT_ratio"], EXIT_CFG
            )
            downgrade_r, downgrade_w = DataAnalysis.calc_linear_kpi(
                kpi_stat["DOWNGRADE_ratio"], DOWNGRADE_CFG
            )
            unactivate_r, unactivate_w = DataAnalysis.calc_linear_kpi(
                kpi_stat["UNACTIVATE_ratio"], UNACTIVATE_CFG
            )
            exception_r, exception_w = DataAnalysis.calc_linear_kpi(
                kpi_stat["EXCEPTION_ratio"], EXCEPTION_CFG
            )
            reliability_s = exit_w + downgrade_w + unactivate_w + exception_w

            # 计算【法规/安全性】模块（不变）
            collision_r, collision_w = DataAnalysis.calc_linear_kpi(
                kpi_stat["COLLISION_ratio"], COLLISION_CFG
            )
            crash_r, crash_w = DataAnalysis.calc_linear_kpi(
                kpi_stat["CRASH_ratio"], CRASH_CFG
            )
            red_green_r, red_green_w = DataAnalysis.calc_red_green_kpi(
                kpi_stat["RED_GREEN_SEVERE"], kpi_stat["RED_GREEN_GENERAL"]
            )
            over_low_r, over_low_w = DataAnalysis.calc_linear_kpi(
                kpi_stat["OVER_LOW_ratio"], OVER_LOW_CFG
            )
            regulationsSafety_s = collision_w + crash_w + red_green_w + over_low_w

            # 计算【舒适性】模块（不变）
            lateral_r, lateral_w = DataAnalysis.calc_linear_kpi(
                kpi_stat["LATERAL_ratio"], LATERAL_CFG
            )
            vertical_r, vertical_w = DataAnalysis.calc_linear_kpi(
                kpi_stat["VERTICAL_ratio"], VERTICAL_CFG
            )
            comfort_s = lateral_w + vertical_w

            # 计算【可用性】模块（使用手动输入的成功率）
            changelane_r, cl_w = DataAnalysis.calc_changelane_kpi(
                change_lane_success_rate,
                kpi_stat["UNAVA_CHANGELANE"],
                CHANGELANE_CFG,
                UNAVA_CHANGELANE_CFG,
            )
            inflow_r, inflow_w = DataAnalysis.calc_linear_kpi(
                inflow_success_rate, INFLOW_CFG
            )
            outflow_r, outflow_w = DataAnalysis.calc_linear_kpi(
                outflow_success_rate, OUTFLOW_CFG
            )
            split_r, split_w = DataAnalysis.calc_linear_kpi(
                diverge_converge_rate, DIVERGE_CONVERGE_CFG
            )
            special_r, special_w = DataAnalysis.calc_linear_kpi(
                special_rate, SPECIAL_CFG
            )
            recog_r, recog_w = DataAnalysis.calc_linear_kpi(recog_rate, RECOG_CFG)
            dropped_r, dropped_w = DataAnalysis.calc_dropped_kpi(kpi_stat["DROPPED"])
            hm_r, hm_w = DataAnalysis.calc_human_machine_kpi(
                kpi_stat["H_M_C"], kpi_stat["H_M_U"]
            )
            mo_r, mo_w = DataAnalysis.calc_micro_oa_kpi(
                kpi_stat["MICRO_OA_FAIL"],
                kpi_stat["MICRO_OA_B"],
                kpi_stat["MICRO_OA_R"],
            )
            usability_s = (
                cl_w
                + inflow_w
                + outflow_w
                + split_w
                + special_w
                + recog_w
                + dropped_w
                + hm_w
                + mo_w
            )

            # 计算总分
            total_s = reliability_s + regulationsSafety_s + comfort_s + usability_s
            total_s_2 = DataAnalysis.format_score(total_s)

            # 更新KpiMain
            main_exists.totalScore = total_s_2
            await db.flush()

            # 更新KpiModule
            module_exists.reliability = reliability_s
            module_exists.regulationsSafety = regulationsSafety_s
            module_exists.comfort = comfort_s
            module_exists.usability = usability_s
            await db.flush()

            # 更新KpiItem
            kpi_items = await db.execute(
                select(KpiItem).where(KpiItem.module_id == module_exists.id)
            )
            kpi_items = list(kpi_items.scalars().all())

            kpi_score_map = {
                "exit": (exit_r, exit_w),
                "downgrade": (downgrade_r, downgrade_w),
                "unactivate": (unactivate_r, unactivate_w),
                "exception": (exception_r, exception_w),
                "collision": (collision_r, collision_w),
                "crash": (crash_r, crash_w),
                "red_green": (red_green_r, red_green_w),
                "over_low": (over_low_r, over_low_w),
                "lateral": (lateral_r, lateral_w),
                "vertical": (vertical_r, vertical_w),
                "change_lane_s": (changelane_r, cl_w),
                "inflow_s": (inflow_r, inflow_w),
                "outflow_s": (outflow_r, outflow_w),
                "diverge_converge_s": (split_r, split_w),
                "special_s": (special_r, special_w),
                "dropped_s": (dropped_r, dropped_w),
                "recog_s": (recog_r, recog_w),
                "hm_s": (hm_r, hm_w),
                "mo_s": (mo_r, mo_w),
            }

            kpi_mpi_map = {
                "exit": kpi_stat["EXIT_ratio"],
                "downgrade": kpi_stat["DOWNGRADE_ratio"],
                "unactivate": kpi_stat["UNACTIVATE_ratio"],
                "exception": kpi_stat["EXCEPTION_ratio"],
                "collision": kpi_stat["COLLISION_ratio"],
                "crash": kpi_stat["CRASH_ratio"],
                "red_green": kpi_stat["RED_GREEN_SEVERE"]
                + kpi_stat["RED_GREEN_GENERAL"],
                "over_low": kpi_stat["OVER_LOW_ratio"],
                "lateral": kpi_stat["LATERAL_ratio"],
                "vertical": kpi_stat["VERTICAL_ratio"],
                "change_lane_s": change_lane_success_rate,
                "inflow_s": inflow_success_rate,
                "outflow_s": outflow_success_rate,
                "diverge_converge_s": diverge_converge_rate,
                "special_s": special_rate,
                "dropped_s": kpi_stat["DROPPED_ratio"],
                "recog_s": recog_rate,
                "hm_s": kpi_stat["H_M_C"] + kpi_stat["H_M_U"],
                "mo_s": kpi_stat["MICRO_OA_FAIL"]
                + kpi_stat["MICRO_OA_B"]
                + kpi_stat["MICRO_OA_R"],
            }

            for item in kpi_items:
                kpi_type = (
                    item.KPIType.lower()
                    if isinstance(item.KPIType, str)
                    else str(item.KPIType).lower()
                )
                if kpi_type in kpi_score_map:
                    item.RawScore = kpi_score_map[kpi_type][0]
                    item.KPIScore = kpi_score_map[kpi_type][1]
                if kpi_type in kpi_mpi_map:
                    item.MPI = kpi_mpi_map[kpi_type]

            await db.commit()
            return "success"

        except Exception as e:
            await db.rollback()
            return f"更新失败，错误信息: {str(e)}"

    @staticmethod
    async def delete_analysis_data(db: AsyncSession, analysis_id: int):
        if not analysis_id:
            return "分析数据ID不能为空"
        stmt = await db.get(KpiMain, analysis_id)
        if not stmt:
            return "分析数据不存在"
        stmt.is_del = True
        await db.commit()
        await db.refresh(stmt)
        return "success"

    # ====================== 可视化统计接口 ======================
    @staticmethod
    async def get_analysis_overview(
        db: AsyncSession,
        project: str = None,
        carModel: str = None,
        funcMode: str = None,
    ):
        """获取分析数据总览统计：总记录数、平均KPI里程、平均总分、最高总分"""
        stmt = select(
            func.count(KpiMain.id).label("total_records"),
            func.avg(KpiMain.kpiMileage).label("avg_mileage"),
            func.avg(KpiMain.totalScore).label("avg_score"),
            func.max(KpiMain.totalScore).label("max_score"),
        ).filter(KpiMain.is_del == False)

        if project:
            stmt = stmt.filter(KpiMain.project.contains(project))
        if carModel:
            stmt = stmt.filter(KpiMain.carModel == carModel)
        if funcMode:
            stmt = stmt.filter(KpiMain.funcMode == funcMode)

        result = await db.execute(stmt)
        row = result.one()

        return {
            "total_records": int(row.total_records or 0),
            "avg_mileage": round(float(row.avg_mileage or 0), 2),
            "avg_score": round(float(row.avg_score or 0), 2),
            "max_score": round(float(row.max_score or 0), 2),
        }

    @staticmethod
    async def get_projects(db: AsyncSession):
        """获取所有项目名称列表"""
        stmt = select(func.distinct(KpiMain.project)).filter(KpiMain.is_del == False)
        result = await db.execute(stmt)
        return [row[0] for row in result.all() if row[0]]

    @staticmethod
    async def get_version_stats(
        db: AsyncSession,
        project: str = None,
        carModel: str = None,
        funcMode: str = None,
    ):
        """获取版本得分统计（可按项目名称筛选）"""
        stmt = select(
            KpiMain.project,
            KpiMain.version,
            KpiMain.funcMode,
            func.avg(KpiMain.totalScore).label("avg_score"),
            func.sum(KpiMain.kpiMileage).label("total_mileage"),
            func.count(KpiMain.id).label("record_count"),
        ).filter(KpiMain.is_del == False)

        if project:
            stmt = stmt.filter(KpiMain.project == project)
        if carModel:
            stmt = stmt.filter(KpiMain.carModel == carModel)
        if funcMode:
            stmt = stmt.filter(KpiMain.funcMode == funcMode)

        stmt = stmt.group_by(
            KpiMain.project, KpiMain.version, KpiMain.funcMode
        ).order_by(KpiMain.project, KpiMain.version)

        result = await db.execute(stmt)
        return [
            {
                "project": row.project,
                "version": row.version,
                "funcMode": row.funcMode,
                "avg_score": round(float(row.avg_score or 0), 2),
                "total_mileage": round(float(row.total_mileage or 0), 2),
                "record_count": int(row.record_count or 0),
            }
            for row in result.all()
        ]

    @staticmethod
    async def delete_analysis_data(db: AsyncSession, analysis_id: int):
        if not analysis_id:
            return "分析数据ID不能为空"
        stmt = await db.get(KpiMain, analysis_id)
        if not stmt:
            return "分析数据不存在"
        stmt.is_del = True
        await db.commit()
        await db.refresh(stmt)
        return "success"


# 实例化
dataAnalysis = DataAnalysis()
