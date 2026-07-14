<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import dayjs from "dayjs";
import { hasAuth } from "@/router/utils";
import { useRole } from "./hook";
import { PureTableBar } from "@/components/RePureTableBar";
import { useRenderIcon } from "@/components/ReIcon/src/hooks";
import { ReAdvancedSearch } from "@/components/ReAdvancedSearch";
import type { FilterItem, SelectOption } from "@/components/ReAdvancedSearch";
import { getVehicleModels, getVinList } from "@/api/system";

import Delete from "~icons/ep/delete";
import Edit from "~icons/ep/edit";
import View from "~icons/ep/view";
import Refresh from "~icons/ep/refresh";
import Plus from "~icons/ep/plus";
import ArrowDown from "~icons/ep/arrow-down";
import Upload from "~icons/ep/upload";
import Check from "~icons/ep/check";
import Close from "~icons/ep/close";
import ResourceDialog from "./dialog.vue";
import ChartCreateDialog from "./ChartCreateDialog.vue";
import BorrowDialog from "../borrow/dialog.vue";

defineOptions({
  name: "VehicleResource"
});

const formRef = ref();
const tableRef = ref();
const advancedSearchRef = ref();
const resourceDialogRef = ref<InstanceType<typeof ResourceDialog>>();
const chartCreateDialogRef = ref<InstanceType<typeof ChartCreateDialog>>();
const borrowDialogRef = ref<InstanceType<typeof BorrowDialog>>();

// 重置：清空表单 + 高级搜索条件
const handleReset = () => {
  resetForm(formRef.value);
  advancedFilters.value = [];
  advancedSearchRef.value?.clearFilters();
};

// 高级搜索
const advancedFilters = ref<FilterItem[]>([]);
const modelOptions = ref<string[]>([]);
const vinOptions = ref<string[]>([]);
let vinSearchTimer: ReturnType<typeof setTimeout> | null = null;

async function fetchModelOptions() {
  try {
    const res: any = await getVehicleModels();
    if (Array.isArray(res.data)) {
      modelOptions.value = res.data;
    }
  } catch (e) {}
}

async function fetchVinOptions(keyword?: string) {
  try {
    const res: any = await getVinList(keyword);
    if (Array.isArray(res.data)) {
      vinOptions.value = res.data;
    }
  } catch (e) {}
}

function handleVinSearch(query: string) {
  if (vinSearchTimer) clearTimeout(vinSearchTimer);
  vinSearchTimer = setTimeout(() => {
    fetchVinOptions(query);
  }, 200);
}

function handleVinFilter(query: string) {
  handleVinSearch(query);
}

function handleVinVisibleChange(visible: boolean) {
  if (visible) {
    handleVinSearch("");
  }
}

onMounted(() => {
  fetchModelOptions();
  fetchVinOptions();
});

const {
  form,
  loading,
  columns,
  dataList,
  pagination,
  selectedNum,
  statistics,
  modelDistributionData,
  modelChartRef,
  customCharts,
  addCustomChart,
  setCustomChartRef,
  removeCustomChart,
  importDialogVisible,
  importLoading,
  importFile,
  onSearch,
  resetForm,
  onbatchDel,
  onDetail,
  onEdit,
  onSave,
  onDelete,
  onAdd,
  onBorrow,
  onBorrowSave,
  onReturnVehicle,
  onCancelBorrow,
  onImport,
  onDownloadTemplate,
  handleFileChange,
  handleFileRemove,
  handleImport,
  handleSizeChange,
  onSelectionCancel,
  handleCurrentChange,
  handleSelectionChange,
  handleSortChange
} = useRole(tableRef, resourceDialogRef, advancedFilters, borrowDialogRef);

// 更多操作命令处理
const handleCommand = (command: string, row: any) => {
  if (command === "detail") {
    onDetail(row);
  } else if (command === "delete") {
    onDelete(row);
  } else if (command === "return") {
    onReturnVehicle(row);
  } else if (command === "cancel") {
    onCancelBorrow(row);
  }
};

// 从表格列动态生成可筛选字段选项（排除勾选列等非数据列）
const filterFieldOptions = computed<SelectOption[]>(() =>
  columns
    .filter((col: any) => col.prop && col.label)
    .map((col: any) => ({ label: col.label, value: col.prop }))
);

// 图表弹窗字段选项（value 使用中文 label，用于统计维度/筛选条件展示）
const chartFieldOptions = computed<SelectOption[]>(() =>
  columns
    .filter((col: any) => col.prop && col.label)
    .map((col: any) => ({ label: col.label, value: col.label }))
);
</script>

<template>
  <div class="main">
    <el-form
      ref="formRef"
      :inline="true"
      :model="form"
      class="search-form bg-bg_color w-full pl-8 pt-3"
    >
      <el-form-item label="车型" prop="model">
        <el-select
          v-model="form.model"
          multiple
          placeholder="请选择/搜索车型"
          filterable
          clearable
          class="w-42.5!"
          collapse-tags
          collapse-tags-tooltip
          :max-collapse-tags="1"
        >
          <el-option v-for="m in modelOptions" :key="m" :label="m" :value="m" />
        </el-select>
      </el-form-item>
      <el-form-item label="VIN 码" prop="vin_code">
        <el-select
          v-model="form.vin_code"
          placeholder="请选择VIN号"
          filterable
          :filter-method="handleVinFilter"
          clearable
          class="w-42.5!"
          @visible-change="handleVinVisibleChange"
        >
          <el-option
            v-for="vin in vinOptions"
            :key="vin"
            :label="vin"
            :value="vin"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="组别" prop="group">
        <el-select
          v-model="form.group"
          placeholder="请选择组别"
          clearable
          class="w-37.5!"
        >
          <el-option label="行车组" value="行车组" />
          <el-option label="泊车组" value="泊车组" />
          <el-option label="预警组" value="预警组" />
        </el-select>
      </el-form-item>
      <el-form-item label="使用状态" prop="vehicle_status">
        <el-select
          v-model="form.vehicle_status"
          placeholder="请选择状态"
          clearable
          class="w-37.5!"
        >
          <el-option label="可借用" value="可借用" />
          <el-option label="已借出" value="已借出" />
          <el-option label="维护中" value="维护中" />
          <el-option label="已预定" value="已预定" />
        </el-select>
      </el-form-item>
      <el-form-item label="车辆状态" prop="test_status">
        <el-select
          v-model="form.test_status"
          placeholder="请选择车辆状态"
          clearable
          class="w-42.5!"
        >
          <el-option label="支持全部测试" value="支持全部测试" />
          <el-option label="不支持泊车测试" value="不支持泊车测试" />
          <el-option label="不支持行车测试" value="不支持行车测试" />
          <el-option label="不支持后向预警测试" value="不支持后向预警测试" />
          <el-option label="不支持全部测试" value="不支持全部测试" />
          <el-option label="生产中" value="生产中" />
          <el-option label="外借中" value="外借中" />
        </el-select>
      </el-form-item>
      <!-- 高级搜索 + 按钮 -->
      <el-form-item>
        <div class="flex items-center gap-4">
          <ReAdvancedSearch
            ref="advancedSearchRef"
            v-model="advancedFilters"
            :field-options="filterFieldOptions"
            @search="onSearch"
          />
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
      title="车辆资源管理"
      :columns="columns"
      tableKey="resource-record"
      @refresh="onSearch"
    >
      <template #buttons>
        <div class="flex justify-end flex-1 gap-2">
          <el-button
            v-if="hasAuth('vehicle:add')"
            type="success"
            :icon="useRenderIcon(Upload)"
            @click="onImport"
          >
            批量导入
          </el-button>
          <el-button
            v-if="hasAuth('vehicle:add')"
            type="primary"
            :icon="useRenderIcon(Plus)"
            @click="onAdd()"
          >
            新增
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
        <!-- adaptive
          :adaptiveConfig="{ offsetBottom: 200 }" -->
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
            color: 'var(--el-text-color-primary)',
            whiteSpace: 'nowrap'
          }"
          @selection-change="handleSelectionChange"
          @page-size-change="handleSizeChange"
          @page-current-change="handleCurrentChange"
          @sort-change="handleSortChange"
          tableKey="resource-record"
          border
        >
          <template #remarks="{ row }">
            <el-tooltip
              v-if="row.remarks && row.remarks.length > 10"
              :content="row.remarks"
              placement="top"
              :popper-style="{ maxWidth: '300px' }"
            >
              <div class="truncate">{{ row.remarks }}</div>
            </el-tooltip>
            <div v-else-if="row.remarks">
              {{ row.remarks }}
            </div>
            <div v-else>-</div>
          </template>
          <template #operation="{ row }">
            <div class="flex items-center justify-center gap-2">
              <el-tooltip
                :content="
                  row.temp_plate_expire_date &&
                  dayjs(row.temp_plate_expire_date).isBefore(dayjs())
                    ? '临牌已到期，无法借用'
                    : ''
                "
                placement="top"
                :disabled="
                  !(
                    row.temp_plate_expire_date &&
                    dayjs(row.temp_plate_expire_date).isBefore(dayjs())
                  )
                "
              >
                <el-button
                  v-if="hasAuth('borrow:add')"
                  class="reset-margin outline-hidden!"
                  link
                  :type="
                    row.temp_plate_expire_date &&
                    dayjs(row.temp_plate_expire_date).isBefore(dayjs())
                      ? 'info'
                      : 'success'
                  "
                  :size="size"
                  :icon="useRenderIcon('ep/position')"
                  :disabled="
                    row.temp_plate_expire_date &&
                    dayjs(row.temp_plate_expire_date).isBefore(dayjs())
                  "
                  @click="onBorrow(row)"
                >
                  借用
                </el-button>
              </el-tooltip>
              <el-button
                v-if="hasAuth('vehicle:update')"
                class="reset-margin outline-hidden! ml-0!"
                link
                type="primary"
                :size="size"
                :icon="useRenderIcon(Edit)"
                @click="onEdit(row)"
              >
                编辑
              </el-button>
              <el-dropdown
                trigger="hover"
                @command="(cmd: string) => handleCommand(cmd, row)"
              >
                <el-button
                  class="reset-margin outline-hidden!"
                  link
                  type="primary"
                  :size="size"
                >
                  更多操作
                  <el-icon class="ml-1"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="detail">
                      <el-icon class="mr-1"
                        ><component :is="useRenderIcon(View)"
                      /></el-icon>
                      详情
                    </el-dropdown-item>
                    <el-dropdown-item
                      v-if="hasAuth('vehicle:delete')"
                      command="delete"
                      divided
                    >
                      <el-icon
                        class="mr-1"
                        style="color: var(--el-color-danger)"
                        ><component :is="useRenderIcon(Delete)"
                      /></el-icon>
                      <span style="color: var(--el-color-danger)">删除</span>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </pure-table>
      </template>
    </PureTableBar>

    <!-- 统计卡片 -->
    <div class="mt-4 grid grid-cols-5 gap-4">
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          车辆总数
        </div>
        <div class="text-2xl font-bold">{{ statistics.total }}</div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          当前可用
        </div>
        <div class="text-2xl font-bold text-[#67C23A]">
          {{ statistics.available }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          已借出
        </div>
        <div class="text-2xl font-bold text-[#409EFF]">
          {{ statistics.borrowed }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          维护中
        </div>
        <div class="text-2xl font-bold text-[#E6A23C]">
          {{ statistics.maintenance }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          已预定
        </div>
        <div class="text-2xl font-bold text-[#909399]">
          {{ statistics.reserved }}
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <!-- <div class="mt-4 flex items-center justify-between">
      <div class="text-base font-medium">车型分布</div>
      <el-button
        type="primary"
        :icon="useRenderIcon('ep/pie-chart')"
        @click="chartCreateDialogRef?.open()"
      >
        新增图表
      </el-button>
    </div> -->
    <div class="mt-4 grid grid-cols-1 gap-4 pb-4">
      <!-- 车型分布柱状图 -->
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-base font-medium mb-4">车型分布</div>
        <div ref="modelChartRef" class="h-84" />
      </div>
      <!-- 自定义图表 -->
      <div
        v-for="chart in customCharts"
        :key="chart.id"
        class="bg-bg_color p-4 rounded shadow relative"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="text-base font-medium">{{ chart.config.name }}</div>
          <el-button
            type="danger"
            link
            :icon="useRenderIcon('ep/delete')"
            @click="removeCustomChart(chart.id)"
          />
        </div>
        <div
          :ref="el => el && setCustomChartRef(chart.id, el as HTMLElement)"
          class="h-64"
        />
      </div>
    </div>

    <!-- 车辆资源弹窗 -->
    <ResourceDialog ref="resourceDialogRef" @save="onSave" />
    <!-- 新建图表弹窗 -->
    <ChartCreateDialog
      ref="chartCreateDialogRef"
      :field-options="chartFieldOptions"
      @add="addCustomChart"
    />
    <!-- 车辆借用弹窗 -->
    <BorrowDialog ref="borrowDialogRef" @save="onBorrowSave" />

    <!-- 批量导入弹窗 -->
    <el-dialog
      v-model="importDialogVisible"
      width="500px"
      top="25vh"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <template #header>
        <div class="flex items-center">
          <span class="text-lg font-medium">批量导入车辆资源</span>
          <el-link
            type="primary"
            :underline="false"
            @click="onDownloadTemplate"
            class="text-sm ml-4"
          >
            下载默认模板
          </el-link>
        </div>
      </template>
      <div class="px-2">
        <el-upload
          v-if="!importFile"
          drag
          :auto-upload="false"
          :limit="1"
          :multiple="false"
          accept=".xlsx,.xls"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
        >
          <div class="el-upload__text">
            将Excel文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              仅支持 .xlsx / .xls 格式的Excel文件
            </div>
          </template>
        </el-upload>
        <div v-else class="flex items-center gap-2 p-3 bg-gray-50 rounded">
          <el-icon class="text-green-500"
            ><component :is="useRenderIcon('ep/document')"
          /></el-icon>
          <span class="flex-1 truncate">{{ importFile.name }}</span>
          <el-button type="danger" text size="small" @click="handleFileRemove">
            移除
          </el-button>
        </div>
        <el-alert
          class="mt-4"
          title="说明：上传Excel文件后，系统将自动读取并导入车辆数据。导入过程中会自动进行数据校验和去重。"
          type="info"
          :closable="false"
          show-icon
        />
      </div>

      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="importLoading"
          :disabled="!importFile"
          @click="handleImport"
        >
          导入
        </el-button>
      </template>
    </el-dialog>
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

:deep(.el-table__header th .cell) {
  white-space: nowrap !important;
}
</style>
