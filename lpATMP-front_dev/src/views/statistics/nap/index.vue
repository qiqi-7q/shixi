<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from "vue";
import { useRole } from "./hook";
import { PureTableBar } from "@/components/RePureTableBar";
import { useRenderIcon } from "@/components/ReIcon/src/hooks";
import NapDialog from "./dialog.vue";
import SuccessRateDialog from "./success-rate-dialog.vue";
import {
  compareAnalysis,
  getAnalysisList,
  getAnalysisDetail,
  getAnalysisOverview,
  getAnalysisProjects,
  getVersionStats
} from "@/api/system";
import { message } from "@/utils/message";
import {
  ElDialog,
  ElTable,
  ElTableColumn,
  ElButton,
  ElMessageBox
} from "element-plus";
import { createAnalysis, updateSuccessRate } from "@/api/system";
import { hasAuth } from "@/router/utils";
import dayjs from "dayjs";

import Delete from "~icons/ep/delete";
import Edit from "~icons/ep/edit";
import EditPen from "~icons/ep/edit-pen";
import View from "~icons/ep/view";
import Refresh from "~icons/ep/refresh";
import Plus from "~icons/ep/plus";
import Check from "~icons/ep/check";
import Compare from "~icons/ep/scale-to-original";

defineOptions({
  name: "StatisticsNap"
});

const formRef = ref();
const tableRef = ref();
const napDialogRef = ref<InstanceType<typeof NapDialog>>();
const successRateDialogRef = ref<InstanceType<typeof SuccessRateDialog>>();
const compareDialogVisible = ref(false);
const compareSelectVisible = ref(false);
const compareData = ref<any[]>([]);
const compareLoading = ref(false);
const currentCompareRow = ref<any>(null);
const selectedVersions = ref<any>([]);
const versionList = ref<any[]>([]);
const versionSelectLoading = ref(false);

// 图表项目筛选
const chartProjectFilter = ref("");

// 独立版本对比相关
const independentCompareVisible = ref(false);
const projectList = ref<string[]>([]);
const projectLoading = ref(false);
const compareForm = ref({
  project: "",
  versionIds: [] as number[]
});

const kpiCompareList = [
  { key: "exit", label: "异常退出" },
  { key: "downgrade", label: "异常降级" },
  { key: "unactivate", label: "无法激活" },
  { key: "exception", label: "系统异常" },
  { key: "collision", label: "碰撞风险" },
  { key: "crash", label: "压实线" },
  { key: "red_green", label: "匝道红绿灯" },
  { key: "over_low", label: "超速/低速" },
  { key: "lateral", label: "横向" },
  { key: "vertical", label: "纵向" },
  { key: "change_lane_s", label: "变道成功率" },
  { key: "inflow_s", label: "汇入成功率" },
  { key: "outflow_s", label: "汇出成功率" },
  { key: "diverge_converge_s", label: "分合流" },
  { key: "special_s", label: "特殊场景" },
  { key: "dropped_s", label: "脱手监测" },
  { key: "recog_s", label: "限速识别" },
  { key: "hm_s", label: "人机共驾" },
  { key: "mo_s", label: "微避障" }
];

const handleReset = () => {
  resetForm(formRef.value);
};

const handleOpenDialog = (result: {
  mode: "add" | "edit" | "detail";
  row: any;
}) => {
  napDialogRef.value?.open(result.mode, result.row);
};

const handleDialogSave = () => {
  onSearch();
};

const {
  form,
  loading,
  columns,
  dataList,
  pagination,
  selectedNum,
  statistics,
  versionScoreChartRef,
  projectOptions,
  carTypeOptions,
  softwareVersionOptions,
  onSearch,
  resetForm,
  onbatchDel,
  onDetail,
  onEdit,
  onDelete,
  onAdd,
  handleSizeChange,
  onSelectionCancel,
  handleCurrentChange,
  handleSelectionChange,
  handleProjectClick,
  updateCharts
} = useRole(tableRef);

const handleDetail = (row: any) => {
  handleProjectClick(row);
};

const handleUpdate = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要更新该记录吗？将使用当前数据的项目、车型、版本、功能模式重新创建分析。`,
      "系统提示",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "info",
        draggable: true
      }
    );

    const res: any = await createAnalysis({
      project: row.project,
      model: row.carModel,
      version: row.version,
      funcMode: row.funcMode
    });

    if (res?.code === 200) {
      message("更新成功", { type: "success" });
      onSearch();
    } else {
      message(res?.message || "更新失败", { type: "error" });
    }
  } catch (e) {
    if (e !== "cancel") {
      message("更新失败", { type: "error" });
    }
  }
};

const handleDelete = (row: any) => {
  onDelete(row);
};

const handleUpdateSuccessRate = (row: any) => {
  successRateDialogRef.value?.open(row);
};

const handleCompare = (row: any) => {
  currentCompareRow.value = row;
  selectedVersions.value = [row.id];
  compareSelectVisible.value = true;
  loadVersionList();
};

const loadVersionList = async () => {
  try {
    versionSelectLoading.value = true;
    const res = (await getAnalysisList({
      skip: 0,
      limit: 1000,
      project: currentCompareRow.value.project,
      carModel: currentCompareRow.value.carModel
    })) as any;

    if (res?.code === 200) {
      versionList.value = (res.data || []).filter(
        (item: any) => item.id !== currentCompareRow.value.id
      );
    } else {
      message(res?.message || "获取版本列表失败", { type: "error" });
    }
  } catch (error) {
    message("获取版本列表失败", { type: "error" });
  } finally {
    versionSelectLoading.value = false;
  }
};

const handleVersionSelect = (versionId: number) => {
  const index = selectedVersions.value.indexOf(versionId);
  console.log("selectedVersions:", selectedVersions.value, index, versionId);
  if (index > -1) {
    selectedVersions.value.splice(index, 1);
  } else {
    console.log("selectedVersions:", selectedVersions.value, index);
    if (selectedVersions.value.length >= 2) {
      selectedVersions.value.pop();
      selectedVersions.value.push(versionId);
      // message("最多选择2个版本进行对比", { type: "warning" });
      return;
    } else {
      selectedVersions.value.push(versionId);
    }
  }
};

const executeCompare = async () => {
  if (selectedVersions.value.length < 2) {
    message("请至少选择2个版本进行对比", { type: "warning" });
    return;
  }

  if (selectedVersions.value.length > 2) {
    message("对比接口仅支持2个版本同时对比", { type: "warning" });
    return;
  }

  try {
    compareLoading.value = true;
    compareSelectVisible.value = false;

    const res: any = await compareAnalysis({
      analysis_id1: selectedVersions.value[0],
      analysis_id2: selectedVersions.value[1]
    });

    if (res?.code === 200) {
      compareData.value = res.data || [];
      compareDialogVisible.value = true;
    } else {
      message(res?.message || "版本对比失败", { type: "error" });
    }
  } catch (error) {
    message("版本对比失败", { type: "error" });
  } finally {
    compareLoading.value = false;
  }
};

const getModuleName = (module: any) => {
  const names = [];
  if (module.reliability != null) names.push(`可靠性`);
  if (module.regulationsSafety != null) names.push(`法规/安全性`);
  if (module.comfort != null) names.push(`舒适性`);
  if (module.usability != null) names.push(`可用性`);
  return names.join("、") || "-";
};

const getModuleScore = (data: any, moduleId: number) => {
  const targetModule = data.module_list?.find((m: any) => m.id === moduleId);
  if (!targetModule) return "-";

  const scores = [];
  if (targetModule.reliability != null) scores.push(targetModule.reliability);
  if (targetModule.regulationsSafety != null)
    scores.push(targetModule.regulationsSafety);
  if (targetModule.comfort != null) scores.push(targetModule.comfort);
  if (targetModule.usability != null) scores.push(targetModule.usability);

  return scores.join(", ") || "-";
};

// 对比样式：值高为红色，值低为灰色，相等为默认
const getCompareClass = (field: string, index: number) => {
  if (compareData.value.length < 2) return "";

  const val1 = compareData.value[0]?.[field] ?? 0;
  const val2 = compareData.value[1]?.[field] ?? 0;

  if (val1 === val2) return "";

  const currentVal = compareData.value[index]?.[field] ?? 0;
  const otherVal = index === 0 ? val2 : val1;

  if (currentVal > otherVal) {
    return "compare-higher";
  } else if (currentVal < otherVal) {
    return "compare-lower";
  }
  return "";
};

// 图表项目筛选变化
const onChartProjectChange = () => {
  updateCharts(chartProjectFilter.value);
};

// 打开独立版本对比对话框
const openCompareDialog = () => {
  independentCompareVisible.value = true;
  compareForm.value = {
    project: "",
    versionIds: []
  };
  // await loadProjectList();
};

// 加载项目列表
const loadProjectList = async () => {
  try {
    projectLoading.value = true;
    const res = (await getAnalysisProjects()) as any;

    if (res?.code === 200) {
      projectList.value = res.data?.projects || [];

      // 默认选中第一个项目
      if (projectList.value.length > 0) {
        chartProjectFilter.value = projectList.value[0];
        // 加载第一个项目的图表数据
        nextTick(() => {
          updateCharts(chartProjectFilter.value);
        });
      }
    } else {
      message(res?.message || "获取项目列表失败", { type: "error" });
    }
  } catch (error) {
    message("获取项目列表失败", { type: "error" });
  } finally {
    projectLoading.value = false;
  }
};

// 项目变化时加载版本列表
const onProjectChange = async () => {
  compareForm.value.versionIds = [];
  if (!compareForm.value.project) {
    versionList.value = [];
    return;
  }

  try {
    versionSelectLoading.value = true;
    const res = (await getAnalysisList({
      skip: 0,
      limit: 1000,
      project: compareForm.value.project
    })) as any;

    if (res?.code === 200) {
      versionList.value = res.data || [];
    } else {
      message(res?.message || "获取版本列表失败", { type: "error" });
    }
  } catch (error) {
    message("获取版本列表失败", { type: "error" });
  } finally {
    versionSelectLoading.value = false;
  }
};

// 独立版本选择
const handleIndependentVersionSelect = (versionId: number) => {
  const index = compareForm.value.versionIds.indexOf(versionId);
  if (index > -1) {
    compareForm.value.versionIds.splice(index, 1);
  } else {
    if (compareForm.value.versionIds.length >= 2) {
      message("仅支持2个版本同时对比", { type: "warning" });
      return;
    }
    compareForm.value.versionIds.push(versionId);
  }
};

// 执行独立版本对比
const executeIndependentCompare = async () => {
  if (compareForm.value.versionIds.length < 2) {
    message("请选择2个版本进行对比", { type: "warning" });
    return;
  }

  try {
    compareLoading.value = true;
    independentCompareVisible.value = false;

    const res: any = await compareAnalysis({
      analysis_id1: compareForm.value.versionIds[0],
      analysis_id2: compareForm.value.versionIds[1]
    });

    if (res?.code === 200) {
      compareData.value = res.data || [];
      compareDialogVisible.value = true;
    } else {
      message(res?.message || "版本对比失败", { type: "error" });
    }
  } catch (error) {
    message("版本对比失败", { type: "error" });
  } finally {
    compareLoading.value = false;
  }
};

// KPI项对比样式
const getKpiCompareClass = (
  kpiKey: string,
  field: string,
  index: number,
  lowerIsBetter: boolean = false
) => {
  if (compareData.value.length < 2) return "";

  const val1 = compareData.value[0]?.[kpiKey]?.[field] ?? 0;
  const val2 = compareData.value[1]?.[kpiKey]?.[field] ?? 0;

  if (val1 === val2) return "";

  const currentVal = compareData.value[index]?.[kpiKey]?.[field] ?? 0;
  const otherVal = index === 0 ? val2 : val1;

  // 对于次数和MPI，越低越好；对于得分，越高越好
  let isHigher = lowerIsBetter ? currentVal < otherVal : currentVal > otherVal;
  let isLower = lowerIsBetter ? currentVal > otherVal : currentVal < otherVal;

  if (isHigher) {
    return "compare-higher";
  } else if (isLower) {
    return "compare-lower";
  }
  return "";
};

// 页面初始化时加载项目列表
onMounted(() => {
  loadProjectList();
});
</script>

<template>
  <div class="main">
    <el-form
      ref="formRef"
      :model="form"
      class="search-form bg-bg_color w-full pl-8 pt-3 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-x-4"
    >
      <el-form-item label="项目" prop="project">
        <el-select
          v-model="form.project"
          placeholder="请选择项目"
          filterable
          clearable
        >
          <el-option
            v-for="p in projectOptions"
            :key="p"
            :label="p"
            :value="p"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="车型" prop="carModel">
        <el-select
          v-model="form.carModel"
          placeholder="请选择车型"
          filterable
          clearable
        >
          <el-option
            v-for="c in carTypeOptions"
            :key="c"
            :label="c"
            :value="c"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="版本" prop="version">
        <el-select
          v-model="form.version"
          placeholder="请选择或输入版本"
          filterable
          clearable
          allow-create
          default-first-option
        >
          <el-option
            v-for="s in softwareVersionOptions"
            :key="s"
            :label="s"
            :value="s"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="功能模式" prop="funcMode">
        <el-select
          v-model="form.funcMode"
          placeholder="请选择功能模式"
          clearable
        >
          <el-option label="NAP" value="NAP" />
          <el-option label="CNAP" value="CNAP" />
          <el-option label="ACC/LCC" value="ACC/LCC" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <div class="flex items-center gap-2">
          <el-button
            type="primary"
            :icon="useRenderIcon('ri/search-line')"
            :loading="loading"
            @click="onSearch"
          >
            搜索
          </el-button>
          <el-button :icon="useRenderIcon(Refresh)" @click="handleReset">
            重置
          </el-button>
        </div>
      </el-form-item>
    </el-form>

    <PureTableBar
      title="NAP 统计分析"
      :columns="columns"
      @refresh="onSearch"
      tableKey="napTable"
    >
      <template #buttons>
        <div class="flex justify-end flex-1">
          <el-button
            type="primary"
            :icon="useRenderIcon(Compare)"
            @click="openCompareDialog"
          >
            版本对比
          </el-button>
          <el-button
            type="primary"
            :icon="useRenderIcon(Plus)"
            @click="handleOpenDialog(onAdd())"
            v-if="hasAuth('statistics:add')"
          >
            新建统计任务
          </el-button>
        </div>
      </template>
      <template v-slot="{ size, dynamicColumns }">
        <div
          v-if="selectedNum > 0"
          v-motion-fade
          class="bg-(--el-fill-color-light) w-full h-11.5 mb-2 pl-4 flex items-center"
        >
          <div class="flex-auto">
            <span
              style="font-size: var(--el-font-size-base)"
              class="text-[rgba(42,46,54,0.5)] dark:text-[rgba(220,220,242,0.5)]"
            >
              已选 {{ selectedNum }} 项
            </span>
            <el-button type="primary" text @click="onSelectionCancel">
              取消选择
            </el-button>
          </div>
          <el-popconfirm title="是否确认删除?" @confirm="onbatchDel">
            <template #reference>
              <el-button type="danger" text class="mr-1!"> 批量删除 </el-button>
            </template>
          </el-popconfirm>
        </div>
        <pure-table
          ref="tableRef"
          row-key="id"
          align-whole="center"
          table-layout="auto"
          :loading="loading"
          :size="size"
          :data="dataList"
          :columns="dynamicColumns"
          :pagination="{ ...pagination, size }"
          :header-cell-style="{
            background: 'var(--el-fill-color-light)',
            color: 'var(--el-text-color-primary)'
          }"
          @selection-change="handleSelectionChange"
          @page-size-change="handleSizeChange"
          @page-current-change="handleCurrentChange"
          border
        >
          <template #operation="{ row }">
            <div
              class="flex items-center justify-center gap-2 operation-buttons"
            >
              <!-- <el-button
                class="reset-margin outline-hidden!"
                link
                type="primary"
                :size="size"
                :icon="useRenderIcon(Edit)"
                @click="handleUpdate(row)"
              >
                更新
              </el-button> -->
              <el-button
                v-if="hasAuth('statistics:update')"
                class="reset-margin outline-hidden!"
                link
                type="success"
                :size="size"
                :icon="useRenderIcon(EditPen)"
                @click="handleUpdateSuccessRate(row)"
              >
                更新成功率
              </el-button>
              <el-button
                class="reset-margin outline-hidden!"
                link
                type="primary"
                :size="size"
                :icon="useRenderIcon(View)"
                @click="handleDetail(row)"
              >
                详情
              </el-button>
              <el-button
                class="reset-margin outline-hidden!"
                link
                type="primary"
                :size="size"
                :icon="useRenderIcon(Compare)"
                @click="handleCompare(row)"
              >
                版本对比
              </el-button>
              <el-button
                v-if="hasAuth('statistics:delete')"
                class="reset-margin outline-hidden!"
                link
                type="danger"
                :size="size"
                :icon="useRenderIcon(Delete)"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </div>
          </template>
        </pure-table>
      </template>
    </PureTableBar>

    <!-- <div class="mt-4 grid grid-cols-4 gap-4">
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          总记录数
        </div>
        <div class="text-2xl font-bold">{{ statistics.total }}</div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          平均KPI里程
        </div>
        <div class="text-2xl font-bold text-[#409EFF]">
          {{ statistics.avgKpiMileage }} km
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          平均总分
        </div>
        <div class="text-2xl font-bold text-[#67C23A]">
          {{ statistics.avgTotalScore }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          最高总分
        </div>
        <div class="text-2xl font-bold text-[#E6A23C]">
          {{ statistics.maxTotalScore }}
        </div>
      </div>
    </div> -->

    <div class="mt-4 grid grid-cols-1 gap-4 pb-4">
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="flex items-center mb-4">
          <div
            class="text-base font-medium"
            style="white-space: nowrap; margin-right: 10px"
          >
            项目统计情况
          </div>
          <div style="max-width: 200px">
            <el-select
              v-model="chartProjectFilter"
              placeholder="选择项目筛选"
              filterable
              clearable
              @change="onChartProjectChange"
              class="w-10"
            >
              <el-option
                v-for="project in projectList"
                :key="project"
                :label="project"
                :value="project"
              />
            </el-select>
          </div>
        </div>
        <div ref="versionScoreChartRef" class="h-80"></div>
      </div>
    </div>

    <NapDialog ref="napDialogRef" @save="handleDialogSave" />

    <!-- 独立版本对比对话框 -->
    <el-dialog
      v-model="independentCompareVisible"
      title="版本对比"
      width="700px"
      :close-on-click-modal="false"
    >
      <div class="independent-compare-container">
        <el-form label-width="80px">
          <el-form-item label="选择项目">
            <el-select
              v-model="compareForm.project"
              placeholder="请选择项目"
              filterable
              clearable
              :loading="projectLoading"
              @change="onProjectChange"
              class="w-full"
            >
              <el-option
                v-for="project in projectList"
                :key="project"
                :label="project"
                :value="project"
              />
            </el-select>
          </el-form-item>
        </el-form>

        <div v-if="compareForm.project" class="version-selection-section">
          <div class="section-title">
            选择版本（已选 {{ compareForm.versionIds.length }}/2）
          </div>
          <div v-loading="versionSelectLoading" class="version-grid">
            <el-empty
              v-if="versionList.length === 0"
              description="该项目暂无版本"
            />
            <div
              v-for="version in versionList"
              :key="version.id"
              class="version-card"
              :class="{ selected: compareForm.versionIds.includes(version.id) }"
              @click="handleIndependentVersionSelect(version.id)"
            >
              <div class="version-header">
                <span class="version-name">{{ version.version }}</span>
                <el-icon
                  v-if="compareForm.versionIds.includes(version.id)"
                  class="check-icon"
                >
                  <Check />
                </el-icon>
              </div>
              <div class="version-details">
                <div class="detail-item">
                  <span class="label">功能模式:</span>
                  <span class="value">{{ version.funcMode }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">KPI里程:</span>
                  <span class="value">{{ version.kpiMileage }} km</span>
                </div>
                <div class="detail-item">
                  <span class="label">总分:</span>
                  <span class="value highlight">{{ version.totalScore }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="independentCompareVisible = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="compareForm.versionIds.length !== 2"
          @click="executeIndependentCompare"
        >
          开始对比
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="compareSelectVisible"
      title="选择对比版本"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="compare-select-container">
        <div class="selected-info">
          <el-tag type="primary" size="large" class="mr-2">
            {{ currentCompareRow?.version }} (当前版本)
          </el-tag>
          <span class="text-gray-500"
            >已选择 {{ selectedVersions.length }} 个版本</span
          >
        </div>

        <div v-loading="versionSelectLoading" class="version-list">
          <el-empty
            v-if="versionList.length === 0"
            description="暂无可对比的版本"
          />
          <div
            v-for="version in versionList"
            :key="version.id"
            class="version-item"
            :class="{ selected: selectedVersions.includes(version.id) }"
            @click="handleVersionSelect(version.id)"
          >
            <div class="version-info">
              <div class="version-name">{{ version.version }}</div>
              <div class="version-detail">
                <span>功能模式: {{ version.funcMode }}</span>
                <span>KPI里程: {{ version.kpiMileage }} km</span>
                <span>总分: {{ version.totalScore }}</span>
              </div>
            </div>
            <el-icon
              class="check-icon"
              :class="{ checked: selectedVersions.includes(version.id) }"
            >
              <component
                :is="selectedVersions.includes(version.id) ? 'Check' : 'Plus'"
              />
            </el-icon>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="compareSelectVisible = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="selectedVersions.length < 2"
          @click="executeCompare"
        >
          开始对比 ({{ selectedVersions.length }})
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="compareDialogVisible"
      title="版本参数对比"
      width="90%"
      :close-on-click-modal="false"
      class="compare-dialog"
    >
      <div v-loading="compareLoading" class="compare-container">
        <div v-if="compareData.length > 0" class="compare-table">
          <div class="compare-header">
            <div class="compare-param">参数项</div>
            <div
              v-for="(item, index) in compareData"
              :key="index"
              class="compare-version"
            >
              <div class="version-title">
                {{ item.version }}
                <el-tag
                  v-if="index === 0"
                  type="primary"
                  size="small"
                  class="ml-2"
                  >当前</el-tag
                >
              </div>
            </div>
          </div>

          <div class="compare-body">
            <div class="compare-row">
              <div class="compare-param">项目</div>
              <div
                v-for="(item, index) in compareData"
                :key="index"
                class="compare-value"
              >
                {{ item.project }}
              </div>
            </div>

            <div class="compare-row">
              <div class="compare-param">车型</div>
              <div
                v-for="(item, index) in compareData"
                :key="index"
                class="compare-value"
              >
                {{ item.carModel }}
              </div>
            </div>

            <div class="compare-row">
              <div class="compare-param">版本</div>
              <div
                v-for="(item, index) in compareData"
                :key="index"
                class="compare-value"
              >
                {{ item.version }}
              </div>
            </div>

            <div class="compare-row">
              <div class="compare-param">功能模式</div>
              <div
                v-for="(item, index) in compareData"
                :key="index"
                class="compare-value"
              >
                {{ item.funcMode }}
              </div>
            </div>

            <div class="compare-row highlight">
              <div class="compare-param">KPI里程</div>
              <div
                v-for="(item, index) in compareData"
                :key="index"
                class="compare-value primary"
                :class="getCompareClass('kpiMileage', index)"
              >
                {{ item.kpiMileage }} km
              </div>
            </div>

            <div class="compare-row highlight">
              <div class="compare-param">总分</div>
              <div
                v-for="(item, index) in compareData"
                :key="index"
                class="compare-value primary large"
                :class="getCompareClass('totalScore', index)"
              >
                {{ item.totalScore }}
              </div>
            </div>

            <div class="compare-section">
              <div class="section-title">模块得分</div>

              <div class="compare-row">
                <div class="compare-param">可靠性</div>
                <div
                  v-for="(item, index) in compareData"
                  :key="index"
                  class="compare-value"
                  :class="getCompareClass('reliability', index)"
                >
                  {{ item.reliability ?? "-" }}
                </div>
              </div>

              <div class="compare-row">
                <div class="compare-param">法规/安全性</div>
                <div
                  v-for="(item, index) in compareData"
                  :key="index"
                  class="compare-value"
                  :class="getCompareClass('regulationsSafety', index)"
                >
                  {{ item.regulationsSafety ?? "-" }}
                </div>
              </div>

              <div class="compare-row">
                <div class="compare-param">舒适性</div>
                <div
                  v-for="(item, index) in compareData"
                  :key="index"
                  class="compare-value"
                  :class="getCompareClass('comfort', index)"
                >
                  {{ item.comfort ?? "-" }}
                </div>
              </div>

              <div class="compare-row">
                <div class="compare-param">可用性</div>
                <div
                  v-for="(item, index) in compareData"
                  :key="index"
                  class="compare-value"
                  :class="getCompareClass('usability', index)"
                >
                  {{ item.usability ?? "-" }}
                </div>
              </div>
            </div>

            <div class="compare-section">
              <div class="section-title">KPI项详细对比</div>

              <div
                v-for="kpi in kpiCompareList"
                :key="kpi.key"
                class="compare-row"
              >
                <div class="compare-param">{{ kpi.label }}</div>
                <div
                  v-for="(item, index) in compareData"
                  :key="index"
                  class="compare-value kpi-cell"
                >
                  <div
                    class="kpi-detail"
                    :class="
                      getKpiCompareClass(kpi.key, 'KPICount', index, true)
                    "
                  >
                    <span class="kpi-label">次数:</span>
                    {{ item[kpi.key]?.KPICount ?? 0 }}
                  </div>
                  <div
                    class="kpi-detail"
                    :class="getKpiCompareClass(kpi.key, 'MPI', index, true)"
                  >
                    <span class="kpi-label">MPI:</span>
                    {{ item[kpi.key]?.MPI ?? 0 }}
                  </div>
                  <div
                    class="kpi-detail"
                    :class="getKpiCompareClass(kpi.key, 'RawScore', index)"
                  >
                    <span class="kpi-label">原始得分:</span>
                    {{ item[kpi.key]?.RawScore ?? 0 }}
                  </div>
                  <div
                    class="kpi-detail"
                    :class="getKpiCompareClass(kpi.key, 'KPIScore', index)"
                  >
                    <span class="kpi-label">加权得分:</span>
                    {{ item[kpi.key]?.KPIScore ?? 0 }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无对比数据" />
      </div>
      <template #footer>
        <el-button @click="compareDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <SuccessRateDialog ref="successRateDialogRef" @save="onSearch" />
  </div>
</template>

<style lang="scss" scoped>
.main-content {
  margin: 24px 24px 0 !important;
}

.search-form {
  :deep(.el-form-item) {
    margin-bottom: 12px;
  }
}

.compare-select-container {
  .selected-info {
    margin-bottom: 16px;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 4px;
    display: flex;
    align-items: center;
  }

  .version-list {
    max-height: 400px;
    overflow-y: auto;

    .version-item {
      padding: 12px;
      margin-bottom: 8px;
      border: 1px solid #dcdfe6;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.3s;
      display: flex;
      justify-content: space-between;
      align-items: center;

      &:hover {
        border-color: #409eff;
        background: #ecf5ff;
      }

      &.selected {
        border-color: #409eff;
        background: #ecf5ff;
      }

      .version-info {
        flex: 1;

        .version-name {
          font-size: 16px;
          font-weight: 500;
          margin-bottom: 4px;
        }

        .version-detail {
          font-size: 13px;
          color: #909399;
          display: flex;
          gap: 16px;
        }
      }

      .check-icon {
        font-size: 20px;
        color: #c0c4cc;

        &.checked {
          color: #409eff;
        }
      }
    }
  }
}

.compare-container {
  min-height: 200px;
  padding: 10px 0;
}

.compare-table {
  .compare-header {
    display: flex;
    background: #f5f7fa;
    border-bottom: 2px solid #409eff;
    font-weight: 500;

    .compare-param {
      width: 150px;
      padding: 16px 12px;
      border-right: 1px solid #ebeef5;
      background: #fafafa;
    }

    .compare-version {
      flex: 1;
      padding: 16px 12px;
      border-right: 1px solid #ebeef5;
      text-align: center;

      &:last-child {
        border-right: none;
      }

      .version-title {
        font-size: 14px;
        font-weight: 500;
        color: #303133;
      }
    }
  }

  .compare-body {
    .compare-row {
      display: flex;
      border-bottom: 1px solid #ebeef5;

      &:hover {
        background: #fafafa;
      }

      &.highlight {
        font-weight: 500;
      }

      .compare-param {
        width: 150px;
        padding: 12px;
        border-right: 1px solid #ebeef5;
        background: #fafafa;
        font-weight: 500;
      }

      .compare-value {
        flex: 1;
        padding: 12px;
        border-right: 1px solid #ebeef5;
        text-align: center;

        &:last-child {
          border-right: none;
        }

        &.primary {
          font-weight: 500;

          &.large {
            font-size: 14px;
          }
        }

        &.kpi-cell {
          text-align: left;
          padding: 8px 12px;

          .kpi-detail {
            font-size: 13px;
            line-height: 1.8;
            color: #606266;

            .kpi-label {
              color: #909399;
              margin-right: 4px;
            }
          }
        }
      }
    }

    .compare-section {
      .section-title {
        padding: 12px;
        background: #f5f7fa;
        font-weight: 500;
        border-bottom: 1px solid #ebeef5;
      }
    }
  }
}

.module-item {
  margin-bottom: 8px;

  .module-name {
    font-size: 13px;
    color: var(--el-text-color-regular);
    line-height: 1.5;
  }
}

.operation-buttons {
  :deep(.el-button) {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    vertical-align: middle;

    .el-icon {
      display: inline-flex;
      align-items: center;
    }
  }
}

// 对比高亮样式
.compare-higher {
  color: #67c23a !important;
  font-weight: 600;
  background-color: rgba(103, 194, 58, 0.15) !important;
}

.compare-lower {
  color: #f56c6c !important;
  font-weight: 600;
  background-color: rgba(245, 108, 108, 0.15) !important;
}

// 独立版本对比对话框样式
.independent-compare-container {
  min-height: 200px;

  .version-selection-section {
    margin-top: 20px;

    .section-title {
      font-size: 14px;
      font-weight: 500;
      margin-bottom: 12px;
      color: #303133;
    }

    .version-grid {
      padding-top: 5px;
      max-height: 400px;
      overflow-y: auto;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 12px;

      .version-card {
        padding: 12px;
        border: 2px solid #dcdfe6;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s;
        background: #fff;

        &:hover {
          border-color: #409eff;
          background: #ecf5ff;
          transform: translateY(-2px);
          box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
        }

        &.selected {
          border-color: #409eff;
          background: #ecf5ff;
          box-shadow: 0 2px 12px rgba(64, 158, 255, 0.3);

          .version-header .check-icon {
            opacity: 1;
          }
        }

        .version-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;

          .version-name {
            font-size: 16px;
            font-weight: 500;
            color: #303133;
          }

          .check-icon {
            font-size: 20px;
            color: #409eff;
            opacity: 0;
            transition: opacity 0.3s;
          }
        }

        .version-details {
          .detail-item {
            font-size: 13px;
            margin-bottom: 4px;
            display: flex;
            justify-content: space-between;

            .label {
              color: #909399;
            }

            .value {
              color: #606266;
              font-weight: 500;

              &.highlight {
                color: #409eff;
                font-size: 14px;
              }
            }
          }
        }
      }
    }
  }
}
</style>
