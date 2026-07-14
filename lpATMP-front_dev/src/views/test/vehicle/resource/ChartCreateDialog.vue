<script setup lang="ts">
import { ref, computed, watch, nextTick, onBeforeUnmount } from "vue";
import { useRenderIcon } from "@/components/ReIcon/src/hooks";
import { ReAdvancedSearch } from "@/components/ReAdvancedSearch";
import type { FilterItem, SelectOption } from "@/components/ReAdvancedSearch";
import * as echarts from "echarts/core";
import { PieChart, BarChart, LineChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([
  PieChart,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  CanvasRenderer
]);

defineOptions({ name: "ChartCreateDialog" });

const props = withDefaults(
  defineProps<{
    fieldOptions?: SelectOption[];
  }>(),
  {
    fieldOptions: () => []
  }
);

const emit = defineEmits<{
  (e: "add", config: ChartConfig): void;
}>();

interface ChartConfig {
  type: string;
  name: string;
  topN: number | null;
  filters: FilterItem[];
  dimension: string;
  sortBy: string;
  sortOrder: string;
  colorScheme: string;
  showDataColumn: boolean;
}

const visible = ref(false);
const previewChartRef = ref<HTMLElement>();
const advancedSearchRef = ref<InstanceType<typeof ReAdvancedSearch>>();
let previewChartInstance: echarts.ECharts | null = null;

// 筛选条件（复用父组件传入的字段选项）
const chartFilters = ref<FilterItem[]>([]);
const chartFilterFieldOptions = computed<SelectOption[]>(() =>
  props.fieldOptions.length
    ? props.fieldOptions
    : dimensionOptions.map(d => ({ label: d, value: d }))
);

// ========== 图表类型 ==========
const chartTypes = [
  { type: "pie", label: "饼图", icon: "ep/pie-chart" },
  { type: "ring", label: "环形图", icon: "ep/more-filled" },
  { type: "bar", label: "柱状图", icon: "ep/histogram" },
  { type: "hbar", label: "条形图", icon: "ep/sort" },
  { type: "line", label: "折线图", icon: "ep/trend-charts" }
];

// ========== 表单数据 ==========
const form = ref<ChartConfig>({
  type: "pie",
  name: "",
  topN: null,
  filters: [],
  dimension: "",
  sortBy: "数值",
  sortOrder: "9-1",
  colorScheme: "色系1",
  showDataColumn: true
});

// ========== 下拉选项（优先使用父组件传入，否则用默认） ==========
const dimensionOptions = computed<string[]>(() =>
  props.fieldOptions.length
    ? props.fieldOptions.map(o => o.value)
    : ["功能", "车型", "组别", "车辆阶段", "使用状态"]
);
const sortByOptions = ["数值", "名称"];
const sortOrderOptions = computed(() => {
  if (form.value.sortBy === "名称") {
    return ["A-Z", "Z-A"];
  }
  return ["9-1", "1-9"];
});

// 排序依据变化时重置排序方向
watch(
  () => form.value.sortBy,
  val => {
    if (val === "名称") {
      form.value.sortOrder = "A-Z";
    } else {
      form.value.sortOrder = "9-1";
    }
  }
);
const colorSchemes = [
  {
    label: "色系1",
    colors: ["#5B8FF9", "#5AD8A6", "#5D7092", "#F6BD16", "#E86452", "#6DC8EC"]
  },
  {
    label: "色系2",
    colors: ["#6DC8EC", "#945FB9", "#FF9845", "#1E9493", "#FF6B81", "#7BED9F"]
  },
  {
    label: "色系3",
    colors: ["#FF99C3", "#FFE0ED", "#C9E9CA", "#87E8C7", "#A0CFFF", "#FFD666"]
  },
  {
    label: "色系4",
    colors: ["#2196F3", "#4CAF50", "#FF9800", "#F44336", "#9C27B0", "#00BCD4"]
  },
  {
    label: "色系5",
    colors: ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#06B6D4"]
  },
  {
    label: "色系6",
    colors: ["#6366F1", "#EC4899", "#14B8A6", "#F97316", "#84CC16", "#A855F7"]
  }
];

const selectedScheme = computed(() =>
  colorSchemes.find(s => s.label === form.value.colorScheme)
);

const currentColors = computed(
  () => colorSchemes.find(s => s.label === form.value.colorScheme)?.colors ?? []
);

// ========== 弹窗控制 ==========
const open = () => {
  form.value = {
    type: "pie",
    name: "",
    topN: null,
    filters: [],
    dimension: dimensionOptions.value[0] ?? "",
    sortBy: "数值",
    sortOrder: "9-1",
    colorScheme: "色系1",
    showDataColumn: true
  };
  chartFilters.value = [];
  advancedSearchRef.value?.clearFilters();
  visible.value = true;
};

const handleClose = () => {
  visible.value = false;
};

const handleAdd = () => {
  if (!form.value.name.trim()) {
    return;
  }
  emit("add", { ...form.value, filters: [...chartFilters.value] });
  visible.value = false;
};

// 筛选条件搜索时刷新预览
const handleFilterSearch = () => {
  if (visible.value) {
    nextTick(() => renderPreview());
  }
};

// ========== 预览图表 ==========
const previewDataMap: Record<string, { name: string; value: number }[]> = {
  功能: [
    { name: "空", value: 2010 },
    { name: "LKA", value: 160 },
    { name: "AEB", value: 134 },
    { name: "FCW", value: 27 },
    { name: "LDW", value: 18 },
    { name: "PARKING", value: 4 }
  ],
  车型: [
    { name: "A7L", value: 12 },
    { name: "ID.4", value: 8 }
  ],
  组别: [
    { name: "行车组", value: 7 },
    { name: "泊车组", value: 8 },
    { name: "预警组", value: 5 }
  ],
  车辆阶段: [
    { name: "DV", value: 6 },
    { name: "PV", value: 5 },
    { name: "PPV", value: 5 },
    { name: "SOP", value: 4 }
  ],
  使用状态: [
    { name: "可用", value: 12 },
    { name: "已外借", value: 5 },
    { name: "维修中", value: 3 }
  ]
};

const currentPreviewData = computed(
  () =>
    previewDataMap[form.value.dimension] ??
    Object.values(previewDataMap)[0] ??
    []
);

function renderPreview() {
  if (!previewChartRef.value) return;
  if (!previewChartInstance) {
    previewChartInstance = echarts.init(previewChartRef.value);
  }
  const colors = currentColors.value;
  const type = form.value.type;

  const previewData = currentPreviewData.value;

  if (type === "pie" || type === "ring") {
    const radius = type === "ring" ? ["40%", "70%"] : "70%";
    previewChartInstance.setOption({
      tooltip: { trigger: "item" },
      legend: { type: "scroll", orient: "vertical", right: 10, top: 20 },
      color: colors,
      series: [
        {
          type: "pie",
          radius,
          center: ["40%", "50%"],
          data: previewData.map((d, i) => ({
            ...d,
            itemStyle: { color: colors[i % colors.length] }
          })),
          label: { show: true, formatter: "{b}: {c}({d}%)" },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: "rgba(0, 0, 0, 0.5)"
            }
          }
        }
      ]
    });
  } else if (type === "bar" || type === "hbar") {
    const isHorizontal = type === "hbar";
    previewChartInstance.setOption({
      tooltip: { trigger: "axis" },
      color: colors,
      grid: { left: 60, right: 20, top: 20, bottom: 40 },
      xAxis: {
        type: isHorizontal ? "value" : "category",
        data: isHorizontal ? undefined : previewData.map(d => d.name)
      },
      yAxis: {
        type: isHorizontal ? "category" : "value",
        data: isHorizontal ? previewData.map(d => d.name) : undefined
      },
      series: [
        {
          type: "bar",
          data: previewData.map((d, i) => ({
            value: d.value,
            itemStyle: { color: colors[i % colors.length] }
          }))
        }
      ]
    });
  } else if (type === "line") {
    previewChartInstance.setOption({
      tooltip: { trigger: "axis" },
      color: colors,
      grid: { left: 60, right: 20, top: 20, bottom: 40 },
      xAxis: { type: "category", data: previewData.map(d => d.name) },
      yAxis: { type: "value" },
      series: [
        {
          type: "line",
          data: previewData.map(d => d.value),
          smooth: true,
          areaStyle: { opacity: 0.3 }
        }
      ]
    });
  } else {
    // 其他类型显示文字提示
    previewChartInstance.setOption({
      title: {
        text: `${chartTypes.find(t => t.type === type)?.label ?? type} 预览`,
        left: "center",
        top: "center",
        textStyle: { fontSize: 16, color: "#999" }
      },
      series: []
    });
  }
}

watch(
  () => [form.value.type, form.value.colorScheme, form.value.dimension],
  () => {
    if (visible.value) {
      nextTick(() => renderPreview());
    }
  }
);

watch(visible, val => {
  if (val) {
    nextTick(() => renderPreview());
  } else {
    if (previewChartInstance) {
      previewChartInstance.dispose();
      previewChartInstance = null;
    }
  }
});

onBeforeUnmount(() => {
  if (previewChartInstance) {
    previewChartInstance.dispose();
  }
});

defineExpose({ open });
</script>

<template>
  <el-dialog
    v-model="visible"
    title="新建图表"
    width="1200px"
    :close-on-click-modal="false"
    destroy-on-close
    @close="handleClose"
  >
    <div class="chart-dialog-body">
      <!-- 左侧配置区 -->
      <div class="chart-config">
        <!-- 图表类型 -->
        <div class="config-section">
          <div class="section-title">图表类型</div>
          <div class="chart-type-grid">
            <div
              v-for="item in chartTypes"
              :key="item.type"
              class="chart-type-item"
              :class="{ active: form.type === item.type }"
              @click="form.type = item.type"
            >
              <el-icon :size="22">
                <component :is="useRenderIcon(item.icon)" />
              </el-icon>
              <span class="type-label">{{ item.label }}</span>
            </div>
          </div>
        </div>

        <!-- 表单配置 -->
        <div class="config-section">
          <el-form label-position="top" :model="form">
            <el-form-item label="图表名称">
              <el-input
                v-model="form.name"
                placeholder="请输入图表名称"
                clearable
              />
            </el-form-item>
            <el-form-item label="筛选条件">
              <ReAdvancedSearch
                ref="advancedSearchRef"
                v-model="chartFilters"
                :field-options="chartFilterFieldOptions"
                :trigger-text="`筛选${chartFilters.length ? `(${chartFilters.length})` : ''}`"
                title="图表筛选条件"
                :popover-width="550"
                @search="handleFilterSearch"
              />
            </el-form-item>
            <el-form-item label="显示top数">
              <el-input
                v-model.number="form.topN"
                placeholder="请输入显示top数（不填或0为全部）"
                clearable
              />
            </el-form-item>
            <el-form-item label="统计维度">
              <el-select
                v-model="form.dimension"
                placeholder="请选择统计维度"
                class="w-full!"
              >
                <el-option
                  v-for="opt in dimensionOptions"
                  :key="opt"
                  :label="opt"
                  :value="opt"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="form.showDataColumn">
                显示数量列
              </el-checkbox>
            </el-form-item>
            <el-form-item label="排序依据">
              <div class="sort-row">
                <el-select
                  v-model="form.sortBy"
                  placeholder="请选择"
                  class="flex-1"
                >
                  <el-option
                    v-for="opt in sortByOptions"
                    :key="opt"
                    :label="opt"
                    :value="opt"
                  />
                </el-select>
                <el-select
                  v-model="form.sortOrder"
                  :placeholder="sortOrderOptions[0]"
                  class="sort-order-select"
                >
                  <el-option
                    v-for="opt in sortOrderOptions"
                    :key="opt"
                    :label="opt"
                    :value="opt"
                  />
                </el-select>
              </div>
            </el-form-item>
            <el-form-item label="图表色系">
              <el-select
                v-model="form.colorScheme"
                placeholder="请选择色系"
                class="w-full! color-scheme-select"
              >
                <template #prefix>
                  <div v-if="selectedScheme" class="color-prefix-blocks">
                    <span
                      v-for="(c, idx) in selectedScheme.colors"
                      :key="idx"
                      class="color-prefix-block"
                      :style="{ background: c }"
                    />
                  </div>
                </template>
                <el-option
                  v-for="scheme in colorSchemes"
                  :key="scheme.label"
                  :label="scheme.label"
                  :value="scheme.label"
                >
                  <div class="color-option-row">
                    <div class="color-option-blocks">
                      <span
                        v-for="(c, idx) in scheme.colors"
                        :key="idx"
                        class="color-option-block"
                        :style="{ background: c }"
                      />
                    </div>
                    <span>{{ scheme.label }}</span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <!-- 右侧预览区 -->
      <div class="chart-preview">
        <div class="preview-header">
          <span class="preview-dot" />
          <span class="preview-title">配置参数预览效果</span>
        </div>
        <div ref="previewChartRef" class="preview-chart" />
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button class="cancel-btn" @click="handleClose">取消</el-button>
        <el-button type="primary" class="add-btn" @click="handleAdd"
          >添加</el-button
        >
      </div>
    </template>
  </el-dialog>
</template>

<style lang="scss" scoped>
.chart-dialog-body {
  display: flex;
  gap: 0;
  min-height: 540px;
  margin: -4px -8px;
}

.chart-config {
  width: 380px;
  flex-shrink: 0;
  overflow-y: auto;
  padding: 16px 20px 16px 12px;

  .config-section {
    margin-bottom: 16px;
  }

  .section-title {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 10px;
    color: var(--el-text-color-primary);
    padding-left: 8px;
    border-left: 3px solid var(--el-color-primary);
  }

  :deep(.el-form-item) {
    margin-bottom: 14px;
  }

  :deep(.el-form-item__label) {
    font-weight: 500;
    font-size: 13px;
    color: var(--el-text-color-regular);
    padding-bottom: 4px;
  }

  :deep(.el-input__wrapper),
  :deep(.el-select .el-input__wrapper) {
    border-radius: 6px;
    transition: box-shadow 0.25s;
  }

  :deep(.el-checkbox__inner) {
    border-radius: 4px;
  }
}

.chart-type-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;

  .chart-type-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    padding: 10px 4px 8px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.25s ease;
    color: var(--el-text-color-regular);
    background: var(--el-fill-color-lighter);
    border: 1.5px solid transparent;

    &:hover {
      background: var(--el-color-primary-light-9);
      color: var(--el-color-primary);
      border-color: var(--el-color-primary-light-7);
      transform: translateY(-1px);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }

    &.active {
      background: var(--el-color-primary);
      color: #fff;
      border-color: var(--el-color-primary);
      box-shadow: 0 3px 12px rgba(64, 158, 255, 0.35);
      transform: translateY(-1px);
    }

    .type-label {
      font-size: 12px;
      line-height: 1;
      font-weight: 500;
    }
  }
}

.sort-row {
  display: flex;
  gap: 10px;
  width: 100%;

  .sort-order-select {
    width: 110px;
    flex-shrink: 0;
  }
}

.color-option-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.color-option-blocks {
  display: flex;
  gap: 3px;

  .color-option-block {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.06);
  }
}

.color-prefix-blocks {
  display: flex;
  gap: 2px;

  .color-prefix-block {
    width: 12px;
    height: 12px;
    border-radius: 2px;
    box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.06);
  }
}

.chart-preview {
  flex: 1;
  padding: 16px 16px 16px 20px;
  background: var(--el-fill-color-lighter);
  border-radius: 0;

  .preview-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }

  .preview-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--el-color-primary);
    flex-shrink: 0;
  }

  .preview-title {
    font-size: 13px;
    font-weight: 500;
    color: var(--el-text-color-primary);
  }

  .preview-chart {
    width: 100%;
    height: 440px;
    background: var(--el-bg-color);
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  .cancel-btn {
    border-radius: 6px;
    padding: 8px 20px;
  }

  .add-btn {
    border-radius: 6px;
    padding: 8px 24px;
    font-weight: 500;
    box-shadow: 0 2px 6px rgba(64, 158, 255, 0.25);
    transition: all 0.25s;

    &:hover {
      box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
    }
  }
}
</style>
