<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";
import { computed, ref, onMounted } from "vue";
import ArrowLeftLine from "~icons/ri/arrow-left-line";
import Download from "~icons/ep/download";
import { getAnalysisDetail } from "@/api/system";
import { message } from "@/utils/message";
import * as XLSX from "xlsx-js-style";

defineOptions({
  name: "NapProjectDetail"
});

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const detailData = ref<any>(null);

const projectInfo = computed(() => {
  if (!detailData.value) return {};
  return {
    project: detailData.value.project,
    carModel: detailData.value.carModel,
    version: detailData.value.version,
    funcMode: detailData.value.funcMode,
    kpiMileage: detailData.value.kpiMileage,
    totalScore: detailData.value.totalScore
  };
});

const tableData = computed(() => {
  if (!detailData.value) return [];

  const data = detailData.value;

  return [
    {
      dimension: "可靠性（权重：30%）",
      kpiItem: "异常退出",
      scoreRatio: 25,
      indicator0: 400,
      indicator60: 1500,
      indicator100: 4000,
      standard: "0分:0-400公里\n60分:400-1500km\n100分:1500-4000km",
      fullScore: 7.5,
      originalScore: data.exit?.RawScore || 0,
      testResult: data.exit?.MPI || 0,
      weightedScore: data.exit?.KPIScore || 0,
      moduleScore: data.reliability || 0,
      description:
        "0-400公里：得0分\n400-1500km：线性得0-60分\n1500-4000km：线性得60-100分"
    },
    {
      dimension: "可靠性（权重：30%）",
      kpiItem: "异常降级",
      scoreRatio: 25,
      indicator0: 200,
      indicator60: 1000,
      indicator100: 2500,
      standard: "0分:0-200公里\n60分:200-1000km\n100分:1000-2500km",
      fullScore: 7.5,
      originalScore: data.downgrade?.RawScore || 0,
      testResult: data.downgrade?.MPI || 0,
      weightedScore: data.downgrade?.KPIScore || 0,
      moduleScore: data.reliability || 0,
      description:
        "0-200公里：得0分\n200-1000km：线性得0-60分\n1000-2500km：线性得60-100分"
    },
    {
      dimension: "可靠性（权重：30%）",
      kpiItem: "无法激活",
      scoreRatio: 25,
      indicator0: 2500,
      indicator60: 6000,
      indicator100: 20000,
      standard: "0分:0-2500公里\n60分:2500-6000km\n100分:6000-20000km",
      fullScore: 7.5,
      originalScore: data.unactivate?.RawScore || 0,
      testResult: data.unactivate?.MPI || 0,
      weightedScore: data.unactivate?.KPIScore || 0,
      moduleScore: data.reliability || 0,
      description:
        "0-2500公里：得0分\n2500-6000km：线性得0-60分\n6000-20000km：线性得60-100分"
    },
    {
      dimension: "可靠性（权重：30%）",
      kpiItem: "系统异常",
      scoreRatio: 25,
      indicator0: 2500,
      indicator60: 6000,
      indicator100: 20000,
      standard: "0分:0-400公里\n60分:400-1500km\n100分:1500-4000km",
      fullScore: 7.5,
      originalScore: data.exception?.RawScore || 0,
      testResult: data.exception?.MPI || 0,
      weightedScore: data.exception?.KPIScore || 0,
      moduleScore: data.reliability || 0,
      description:
        "0-400公里：得0分\n400-1500km：线性得0-60分\n1500-4000km：线性得60-100分"
    },
    {
      dimension: "法规/安全性（权重：30%）",
      kpiItem: "碰撞风险",
      scoreRatio: 30,
      indicator0: 50,
      indicator60: 100,
      indicator100: 1000,
      standard: "0分:0-50公里\n60分:50-100km\n100分:100-1000km",
      fullScore: 9,
      originalScore: data.collision?.RawScore || 0,
      testResult: data.collision?.MPI || 0,
      weightedScore: data.collision?.KPIScore || 0,
      moduleScore: data.regulationsSafety || 0,
      description:
        "0-50公里：得0分\n50-100km：线性得0-60分\n100-1000km：线性得60-100分"
    },
    {
      dimension: "法规/安全性（权重：30%）",
      kpiItem: "压实线",
      scoreRatio: 30,
      indicator0: 200,
      indicator60: 500,
      indicator100: 4500,
      standard: "0分:0-200公里\n60分:200-500km\n100分:500-4500km",
      fullScore: 9,
      originalScore: data.crash?.RawScore || 0,
      testResult: data.crash?.MPI || 0,
      weightedScore: data.crash?.KPIScore || 0,
      moduleScore: data.regulationsSafety || 0,
      description:
        "0-200公里：得0分\n200-500km：线性得0-60分\n500-4500km：线性得60-100分"
    },
    {
      dimension: "法规/安全性（权重：30%）",
      kpiItem: "匝道红绿灯",
      scoreRatio: 20,
      indicator0: "-",
      indicator60: "-",
      indicator100: "-",
      standard:
        "严重失效（导致闯红灯）：每次扣5分\n一般失效（错误减速/加速）：每次扣2分",
      fullScore: 6,
      originalScore: data.red_green?.RawScore || 0,
      testResult: data.red_green?.KPICount || 0,
      weightedScore: data.red_green?.KPIScore || 0,
      moduleScore: data.regulationsSafety || 0,
      description:
        "严重失效（导致闯红灯）：每次扣5分\n一般失效（错误减速/加速）：每次扣2分"
    },
    {
      dimension: "法规/安全性（权重：30%）",
      kpiItem: "超速/低速",
      scoreRatio: 20,
      indicator0: 500,
      indicator60: 800,
      indicator100: 3000,
      standard: "0分:0-500公里\n60分:500-800km\n100分:800-3000km",
      fullScore: 6,
      originalScore: data.over_low?.RawScore || 0,
      testResult: data.over_low?.MPI || 0,
      weightedScore: data.over_low?.KPIScore || 0,
      moduleScore: data.regulationsSafety || 0,
      description:
        "0-500公里：得0分\n500-800km：线性得0-60分\n800-3000km：线性得60-100分"
    },
    {
      dimension: "舒适性（权重：20%）",
      kpiItem: "横向",
      scoreRatio: 50,
      indicator0: 50,
      indicator60: 200,
      indicator100: 1000,
      standard: "0分:0-50公里\n60分:50-200km\n100分:200-1000km",
      fullScore: 10,
      originalScore: data.lateral?.RawScore || 0,
      testResult: data.lateral?.MPI || 0,
      weightedScore: data.lateral?.KPIScore || 0,
      moduleScore: data.comfort || 0,
      description:
        "0-50公里：得0分\n50-200km：线性得0-60分\n200-1000km：线性得60-100分"
    },
    {
      dimension: "舒适性（权重：20%）",
      kpiItem: "纵向",
      scoreRatio: 50,
      indicator0: 50,
      indicator60: 200,
      indicator100: 1000,
      standard: "0分:0-50公里\n60分:50-200km\n100分:200-1000km",
      fullScore: 10,
      originalScore: data.vertical?.RawScore || 0,
      testResult: data.vertical?.MPI || 0,
      weightedScore: data.vertical?.KPIScore || 0,
      moduleScore: data.comfort || 0,
      description:
        "0-50公里：得0分\n50-200km：线性得0-60分\n200-1000km：线性得60-100分"
    },
    {
      dimension: "可用性（权重：20%）",
      kpiItem: "变道成功率",
      scoreRatio: 20,
      indicator0: "80%",
      indicator60: "90%",
      indicator100: "99.50%",
      standard:
        "变道成功率=成功变道次数/有效变道请求次数×100%：\n＜80%直接得0分；\n80%-90%：线性得分（0-60分）；\n90%-99.5%：线性得分（60-100分）；\n无效变道（如无必要的反复变道）每出现1次扣5分。",
      fullScore: 4,
      originalScore: data.change_lane_s?.RawScore || 0,
      testResult: data.change_lane_s?.MPI || 0,
      weightedScore: data.change_lane_s?.KPIScore || 0,
      moduleScore: data.usability || 0,
      description:
        "＜80%直接得0分；80%-90%：线性得分（0-60分）；90%-99.5%：线性得分（60-100分）；无效变道每出现1次扣5分"
    },
    {
      dimension: "可用性（权重：20%）",
      kpiItem: "汇入成功率",
      scoreRatio: 20,
      indicator0: "80%",
      indicator60: "90%",
      indicator100: "98%",
      standard:
        "高速/匝道汇入主路场景，成功率=成功汇入次数/需汇入场景数×100%：\n＜80%直接得0分；\n80%-90%：线性得分（0-60分）；\n90%-98%：线性得分（60-100分）",
      fullScore: 4,
      originalScore: data.inflow_s?.RawScore || 0,
      testResult: data.inflow_s?.MPI || 0,
      weightedScore: data.inflow_s?.KPIScore || 0,
      moduleScore: data.usability || 0,
      description:
        "高速/匝道汇入主路场景，＜80%直接得0分；80%-90%：线性得分（0-60分）；90%-98%：线性得分（60-100分）"
    },
    {
      dimension: "可用性（权重：20%）",
      kpiItem: "汇出成功率",
      scoreRatio: 20,
      indicator0: "80%",
      indicator60: "90%",
      indicator100: "98%",
      standard:
        "主路/匝道汇出场景，规则同汇入成功率；\n＜80%直接得0分；\n80%-90%：线性得分（0-60分）；\n90%-98%：线性得分（60-100分）",
      fullScore: 4,
      originalScore: data.outflow_s?.RawScore || 0,
      testResult: data.outflow_s?.MPI || 0,
      weightedScore: data.outflow_s?.KPIScore || 0,
      moduleScore: data.usability || 0,
      description:
        "主路/匝道汇出场景，规则同汇入成功率；＜80%直接得0分；80%-90%：线性得分（0-60分）；90%-98%：线性得分（60-100分）"
    },
    {
      dimension: "可用性（权重：20%）",
      kpiItem: "分合流",
      scoreRatio: 10,
      indicator0: "80%",
      indicator60: "90%",
      indicator100: "98%",
      standard:
        "含高速分道、合流、枢纽场景通过率，按比例线性得分，通过率小于80%得0分；\n80%-90%：线性得分（0-60分）；\n90%-98%：线性得分（60-100分）",
      fullScore: 2,
      originalScore: data.diverge_converge_s?.RawScore || 0,
      testResult: data.diverge_converge_s?.MPI || 0,
      weightedScore: data.diverge_converge_s?.KPIScore || 0,
      moduleScore: data.usability || 0,
      description:
        "含高速分道、合流、枢纽场景通过率，通过率小于80%得0分；80%-90%：线性得分（0-60分）；90%-98%：线性得分（60-100分）"
    },
    {
      dimension: "可用性（权重：20%）",
      kpiItem: "特殊场景",
      scoreRatio: 10,
      indicator0: "60%",
      indicator60: "70%",
      indicator100: "95%",
      standard:
        "通过率=成功通过次数/场景总数×100%，按比例线性得分，通过率小于60%得0分；\n60%-70%：线性得分（0-60分）；\n70%-95%：线性得分（60-100分）",
      fullScore: 2,
      originalScore: data.special_s?.RawScore || 0,
      testResult: data.special_s?.MPI || 0,
      weightedScore: data.special_s?.KPIScore || 0,
      moduleScore: data.usability || 0,
      description:
        "通过率=成功通过次数/场景总数×100%，通过率小于60%得0分；60%-70%：线性得分（0-60分）；70%-95%：线性得分（60-100分）"
    },
    {
      dimension: "可用性（权重：20%）",
      kpiItem: "脱手监测",
      scoreRatio: 5,
      indicator0: "-",
      indicator60: "-",
      indicator100: "-",
      standard: "每出现1次漏判、误判扣5分",
      fullScore: 1,
      originalScore: data.dropped_s?.RawScore || 0,
      testResult: data.dropped_s?.KPICount || 0,
      weightedScore: data.dropped_s?.KPIScore || 0,
      moduleScore: data.usability || 0,
      description: "每出现1次漏判、误判扣5分"
    },
    {
      dimension: "可用性（权重：20%）",
      kpiItem: "限速识别",
      scoreRatio: 5,
      indicator0: "90%",
      indicator60: "95%",
      indicator100: "99.50%",
      standard:
        "含主路、匝道的各类限速牌，识别率=正确识别次数/应识别限速标识次数×100%：\n＜90%直接得0分；\n90%-95%：线性得分（0-60分）；\n95%-99.5%：线性得分（60-100分）",
      fullScore: 1,
      originalScore: data.recog_s?.RawScore || 0,
      testResult: data.recog_s?.MPI || 0,
      weightedScore: data.recog_s?.KPIScore || 0,
      moduleScore: data.usability || 0,
      description:
        "含主路、匝道的各类限速牌，识别率=正确识别次数/应识别限速标识次数×100%：＜90%直接得0分；90%-95%：线性得分（0-60分）；95%-99.5%：线性得分（60-100分）"
    },
    {
      dimension: "可用性（权重：20%）",
      kpiItem: "人机共驾",
      scoreRatio: 5,
      indicator0: "-",
      indicator60: "-",
      indicator100: "-",
      standard:
        "每出现1次接管冲突（系统与驾驶员抢控、拒绝接管）直接0分；接管过程中出现车辆失控风险得0分。",
      fullScore: 1,
      originalScore: data.hm_s?.RawScore || 0,
      testResult: data.hm_s?.KPICount || 0,
      weightedScore: data.hm_s?.KPIScore || 0,
      moduleScore: data.usability || 0,
      description:
        "每出现1次接管冲突（系统与驾驶员抢控、拒绝接管）直接0分；接管过程中出现车辆失控风险得0分"
    },
    {
      dimension: "可用性（权重：20%）",
      kpiItem: "微避障",
      scoreRatio: 5,
      indicator0: "-",
      indicator60: "-",
      indicator100: "-",
      standard:
        "每出现1次避障失败（未避让非机动车/行人/静止障碍物）直接扣5分；\n避障过程中出现急刹/猛打方向每次扣3分；\n避障后无回正、压线，每次扣2分。",
      fullScore: 1,
      originalScore: data.mo_s?.RawScore || 0,
      testResult: data.mo_s?.KPICount || 0,
      weightedScore: data.mo_s?.KPIScore || 0,
      moduleScore: data.usability || 0,
      description:
        "每出现1次避障失败（未避让非机动车/行人/静止障碍物）直接扣5分；避障过程中出现急刹/猛打方向每次扣3分；避障后无回正、压线，每次扣2分"
    }
  ];
});

const totalScore = computed(() => {
  if (!detailData.value) return "0.00";
  return detailData.value.totalScore?.toFixed(2) || "0.00";
});

async function loadDetail() {
  const id = route.params.id;
  if (!id) {
    message("缺少项目ID", { type: "error" });
    return;
  }

  loading.value = true;
  try {
    const res: any = await getAnalysisDetail(Number(id));
    if (res?.code === 200 && res.data) {
      detailData.value = res.data;
    } else {
      message(res?.message || "获取详情失败", { type: "error" });
    }
  } catch (error) {
    message("获取详情失败", { type: "error" });
  } finally {
    loading.value = false;
  }
}

const objectSpanMethod = ({ row, column, rowIndex, columnIndex }) => {
  const dimension = row.dimension;
  const rowCount = tableData.value.filter(
    d => d.dimension === dimension
  ).length;
  const isFirstInGroup =
    rowIndex === 0 || tableData.value[rowIndex - 1].dimension !== dimension;

  if (columnIndex === 0) {
    if (isFirstInGroup) {
      return {
        rowspan: rowCount,
        colspan: 1
      };
    } else {
      return {
        rowspan: 0,
        colspan: 0
      };
    }
  }

  if (columnIndex === 11) {
    if (isFirstInGroup) {
      return {
        rowspan: rowCount,
        colspan: 1
      };
    } else {
      return {
        rowspan: 0,
        colspan: 0
      };
    }
  }
};

const getSummaries = param => {
  const { columns } = param;
  const sums = [];

  columns.forEach((column, index) => {
    if (index === 0) {
      sums[index] = "合计";
      return;
    }

    if (index === 2) {
      sums[index] = "";
      return;
    }

    if (index === 7) {
      sums[index] = "100";
      return;
    }

    if (index === 10) {
      sums[index] = totalScore.value;
      return;
    }

    if (index === 11) {
      sums[index] = totalScore.value;
      return;
    }

    sums[index] = "";
  });

  return sums;
};

const goBack = () => {
  router.push("/statistics/nap");
};

function exportToExcel() {
  if (!detailData.value || tableData.value.length === 0) {
    message("暂无数据可导出", { type: "warning" });
    return;
  }

  try {
    const wb = XLSX.utils.book_new();

    const headerStyle = {
      fill: { fgColor: { rgb: "FFFFFF" } },
      font: { bold: true, color: { rgb: "000000" }, sz: 11 },
      alignment: { horizontal: "center", vertical: "center", wrapText: true },
      border: {
        top: { style: "thin", color: { rgb: "000000" } },
        bottom: { style: "thin", color: { rgb: "000000" } },
        left: { style: "thin", color: { rgb: "000000" } },
        right: { style: "thin", color: { rgb: "000000" } }
      }
    };

    const cellStyle = {
      alignment: { horizontal: "center", vertical: "center", wrapText: true },
      border: {
        top: { style: "thin", color: { rgb: "000000" } },
        bottom: { style: "thin", color: { rgb: "000000" } },
        left: { style: "thin", color: { rgb: "000000" } },
        right: { style: "thin", color: { rgb: "000000" } }
      }
    };

    const centerStyle = {
      ...cellStyle,
      alignment: { horizontal: "center", vertical: "center", wrapText: true }
    };

    const wsData = [
      [
        "评价维度",
        "KPI项",
        "分数占比",
        "指标（0分）",
        "指标（60分）",
        "指标（100分）",
        "参考标准",
        "占比满分",
        "原始得分",
        "测试结果",
        "加权得分",
        "模块得分",
        "评分说明"
      ]
    ];

    tableData.value.forEach(row => {
      wsData.push([
        row.dimension,
        row.kpiItem,
        row.scoreRatio,
        row.indicator0,
        row.indicator60,
        row.indicator100,
        row.standard,
        row.fullScore,
        row.originalScore,
        row.testResult,
        row.weightedScore,
        row.moduleScore,
        row.description
      ]);
    });

    wsData.push([
      "合计",
      "",
      "",
      "",
      "",
      "",
      "",
      "100",
      "",
      "",
      totalScore.value,
      totalScore.value,
      ""
    ]);

    const ws = XLSX.utils.aoa_to_sheet(wsData);

    const range = XLSX.utils.decode_range(ws["!ref"]);

    for (let C = range.s.c; C <= range.e.c; C++) {
      const addr = XLSX.utils.encode_cell({ r: 0, c: C });
      ws[addr].s = headerStyle;
    }

    for (let R = 1; R <= range.e.r; R++) {
      for (let C = range.s.c; C <= range.e.c; C++) {
        const addr = XLSX.utils.encode_cell({ r: R, c: C });
        if (ws[addr]) {
          if (
            C === 2 ||
            C === 3 ||
            C === 4 ||
            C === 5 ||
            C === 7 ||
            C === 8 ||
            C === 9 ||
            C === 10 ||
            C === 11
          ) {
            ws[addr].s = centerStyle;
          } else {
            ws[addr].s = cellStyle;
          }
        }
      }
    }

    ws["!cols"] = [
      { wch: 28 },
      { wch: 18 },
      { wch: 14 },
      { wch: 18 },
      { wch: 18 },
      { wch: 18 },
      { wch: 55 },
      { wch: 14 },
      { wch: 22 },
      { wch: 18 },
      { wch: 20 },
      { wch: 18 },
      { wch: 60 }
    ];

    const merges = [];
    let mergeStart = 1;
    for (let R = 2; R <= range.e.r; R++) {
      const currentDim = wsData[R][0];
      const prevDim = wsData[R - 1][0];
      if (currentDim !== prevDim || R === range.e.r) {
        const mergeEnd = currentDim === prevDim ? R : R - 1;
        if (mergeStart < mergeEnd) {
          merges.push({
            s: { r: mergeStart, c: 0 },
            e: { r: mergeEnd, c: 0 }
          });
          merges.push({
            s: { r: mergeStart, c: 11 },
            e: { r: mergeEnd, c: 11 }
          });
        }
        mergeStart = R;
      }
    }
    ws["!merges"] = merges;

    ws["!rows"] = [];
    for (let R = 0; R <= range.e.r; R++) {
      ws["!rows"][R] = { hpx: R === 0 ? 40 : 60 };
    }

    XLSX.utils.book_append_sheet(wb, ws, "NAP评分详情");

    const fileName = `NAP评分详情_${projectInfo.value.project || "未命名"}_${new Date().toISOString().slice(0, 10)}.xlsx`;
    XLSX.writeFile(wb, fileName);

    message("导出成功", { type: "success" });
  } catch (error) {
    console.error("导出失败:", error);
    message("导出失败", { type: "error" });
  }
}

onMounted(() => {
  loadDetail();
});
</script>

<template>
  <div class="main">
    <el-card shadow="never" class="mb-4" v-loading="loading">
      <div class="flex items-center">
        <div class="flex items-center gap-4" style="margin-right: 20px">
          <el-button @click="goBack" :icon="ArrowLeftLine">返回</el-button>
        </div>
        <div v-if="detailData" class="flex gap-6 text-sm">
          <div>
            <span class="text-[var(--el-text-color-secondary)]">项目：</span>
            <span class="font-medium">{{ detailData.project }}</span>
          </div>
          <div>
            <span class="text-[var(--el-text-color-secondary)]">车型：</span>
            <span class="font-medium">{{ detailData.carModel }}</span>
          </div>
          <div>
            <span class="text-[var(--el-text-color-secondary)]">版本：</span>
            <span class="font-medium">{{ detailData.version }}</span>
          </div>
          <div>
            <span class="text-[var(--el-text-color-secondary)]"
              >功能模式：</span
            >
            <span class="font-medium">{{ detailData.funcMode }}</span>
          </div>
          <div>
            <span class="text-[var(--el-text-color-secondary)]">KPI里程：</span>
            <span class="font-medium">{{ detailData.kpiMileage }} km</span>
          </div>
          <div>
            <span class="text-[var(--el-text-color-secondary)]">总分：</span>
            <span class="font-medium text-[var(--el-color-primary)]">{{
              totalScore
            }}</span>
          </div>
        </div>
      </div>
    </el-card>

    <el-card shadow="never" v-loading="loading">
      <div class="flex justify-end mb-3">
        <el-button type="success" :icon="Download" @click="exportToExcel">
          导出 Excel
        </el-button>
      </div>
      <el-table
        :data="tableData"
        border
        style="width: 100%"
        :span-method="objectSpanMethod"
        max-height="75vh"
        :show-summary="true"
        :summary-method="getSummaries"
        sum-text="合计"
        empty-text="暂无数据"
      >
        <el-table-column
          prop="dimension"
          label="评价维度"
          width="160"
          fixed="left"
        />
        <el-table-column prop="kpiItem" label="KPI项" width="100" />
        <el-table-column
          prop="scoreRatio"
          label="分数占比"
          width="90"
          align="center"
        />
        <el-table-column
          prop="indicator0"
          label="指标（0分）"
          width="100"
          align="center"
        />
        <el-table-column
          prop="indicator60"
          label="指标（60分）"
          width="100"
          align="center"
        />
        <el-table-column
          prop="indicator100"
          label="指标（100分）"
          width="110"
          align="center"
        />
        <el-table-column prop="standard" label="参考标准" min-width="200">
          <template #default="{ row }">
            <div class="whitespace-pre-line">{{ row.standard }}</div>
          </template>
        </el-table-column>
        <el-table-column
          prop="fullScore"
          label="占比满分"
          width="90"
          align="center"
        />
        <el-table-column
          prop="originalScore"
          label="原始得分"
          width="110"
          align="center"
        />
        <el-table-column
          prop="testResult"
          label="测试结果"
          width="100"
          align="center"
        />
        <el-table-column
          prop="weightedScore"
          label="加权得分"
          width="100"
          align="center"
        />
        <el-table-column
          prop="moduleScore"
          label="模块得分"
          width="100"
          align="center"
        />
        <el-table-column prop="description" label="评分说明" min-width="250">
          <template #default="{ row }">
            <div class="whitespace-pre-line">{{ row.description }}</div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style lang="scss" scoped>
.whitespace-pre-line {
  white-space: pre-line;
}
</style>
