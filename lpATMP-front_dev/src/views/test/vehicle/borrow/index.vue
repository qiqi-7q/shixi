<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
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
import Check from "~icons/ep/check";
import Close from "~icons/ep/close";
import BorrowDialog from "./dialog.vue";

defineOptions({
  name: "TestVehicleBorrow"
});

const formRef = ref();
const tableRef = ref();
const advancedSearchRef = ref();
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
  modelChartRef,
  statusChartRef,
  onSearch,
  resetForm,
  onbatchDel,
  onDetail,
  onEdit,
  onDelete,
  onReturn,
  onCancel,
  onSave,
  onAdd,
  handleSizeChange,
  onSelectionCancel,
  handleCurrentChange,
  handleSelectionChange
} = useRole(tableRef, advancedFilters);

// 弹窗打开处理
const handleOpenDialog = (result: {
  mode: "add" | "edit" | "detail";
  row: any;
}) => {
  borrowDialogRef.value?.open(result.mode, result.row);
};

// 更多操作命令处理
const handleCommand = (command: string, row: any) => {
  if (command === "detail") {
    handleOpenDialog(onDetail(row));
  } else if (command === "delete") {
    onDelete(row);
  } else if (command === "return") {
    onReturn(row);
  } else if (command === "cancel") {
    onCancel(row);
  }
};

// 从表格列动态生成可筛选字段选项
const filterFieldOptions = computed<SelectOption[]>(() =>
  columns
    .filter((col: any) => col.prop && col.label)
    .map((col: any) => ({ label: col.label, value: col.prop }))
);
</script>

<template>
  <div class="main">
    <el-form
      ref="formRef"
      :inline="true"
      :model="form"
      class="search-form bg-bg_color w-full pl-8 pt-3 overflow-auto"
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
      <el-form-item label="车辆VIN号" prop="vin_code">
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
      <el-form-item label="借用状态" prop="borrow_status">
        <el-select
          v-model="form.borrow_status"
          placeholder="请选择状态"
          clearable
          class="w-37.5!"
        >
          <el-option label="借用中" value="borrowing" />
          <el-option label="已归还" value="returned" />
          <el-option label="已取消" value="cancelled" />
          <el-option label="已预约" value="reserved" />
        </el-select>
      </el-form-item>
      <el-form-item label="司机姓名" prop="driver_name">
        <el-input
          v-model="form.driver_name"
          placeholder="请输入司机姓名"
          clearable
          class="w-42.5!"
        />
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
      title="车辆借用记录"
      :columns="columns"
      @refresh="onSearch"
      tableKey="borrow-record"
    >
      <!-- <template #buttons>
        <div class="flex justify-end flex-1">
          <el-button
            type="primary"
            :icon="useRenderIcon(Plus)"
            @click="handleOpenDialog(onAdd())"
          >
            新增
          </el-button>
        </div>
      </template> -->
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
              <el-button
                class="reset-margin outline-hidden!"
                link
                :type="
                  row.borrow_status !== 'returned' &&
                  row.borrow_status !== 'cancelled'
                    ? 'success'
                    : 'info'
                "
                :size="size"
                :icon="useRenderIcon(Check)"
                :disabled="
                  row.borrow_status === 'returned' ||
                  row.borrow_status === 'cancelled'
                "
                @click="
                  row.borrow_status !== 'returned' &&
                  row.borrow_status !== 'cancelled' &&
                  handleCommand('return', row)
                "
              >
                归还
              </el-button>
              <el-button
                class="reset-margin outline-hidden!"
                link
                :type="
                  row.borrow_status !== 'returned' &&
                  row.borrow_status !== 'cancelled'
                    ? 'danger'
                    : 'info'
                "
                :size="size"
                :icon="useRenderIcon(Close)"
                :disabled="
                  row.borrow_status === 'returned' ||
                  row.borrow_status === 'cancelled'
                "
                @click="
                  row.borrow_status !== 'returned' &&
                  row.borrow_status !== 'cancelled' &&
                  handleCommand('cancel', row)
                "
              >
                取消
              </el-button>
              <!-- <el-button
                class="reset-margin outline-hidden!"
                link
                type="primary"
                :size="size"
                :icon="useRenderIcon(Edit)"
                @click="handleOpenDialog(onEdit(row))"
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
                    <el-dropdown-item command="delete" divided>
                      <el-icon
                        class="mr-1"
                        style="color: var(--el-color-danger)"
                        ><component :is="useRenderIcon(Delete)"
                      /></el-icon>
                      <span style="color: var(--el-color-danger)">删除</span>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown> -->
            </div>
          </template>
        </pure-table>
      </template>
    </PureTableBar>

    <!-- 统计卡片 -->
    <div class="mt-4 grid grid-cols-5 gap-4">
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-(--el-text-color-secondary) mb-1">
          借用总数
        </div>
        <div class="text-2xl font-bold">{{ statistics.total }}</div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-(--el-text-color-secondary) mb-1">
          借用中
        </div>
        <div class="text-2xl font-bold text-[#409EFF]">
          {{ statistics.borrowing }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-(--el-text-color-secondary) mb-1">
          已归还
        </div>
        <div class="text-2xl font-bold text-[#67C23A]">
          {{ statistics.returned }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-(--el-text-color-secondary) mb-1">
          已取消
        </div>
        <div class="text-2xl font-bold text-[#909399]">
          {{ statistics.cancelled }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-(--el-text-color-secondary) mb-1">
          已预约
        </div>
        <div class="text-2xl font-bold text-[#E6A23C]">
          {{ statistics.reserved }}
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="mt-4 grid grid-cols-1 gap-4 pb-4" v-if="false">
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-base font-medium mb-4">车型分布</div>
        <div ref="modelChartRef" class="h-64"></div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-base font-medium mb-4">借用状态</div>
        <div ref="statusChartRef" class="h-64"></div>
      </div>
    </div>

    <!-- 借用弹窗 -->
    <BorrowDialog ref="borrowDialogRef" @save="onSave" />
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
</style>
