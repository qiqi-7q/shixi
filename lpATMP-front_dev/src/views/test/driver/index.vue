<script setup lang="ts">
import { ref, computed } from "vue";
import { useRole } from "./hook";
import { PureTableBar } from "@/components/RePureTableBar";
import { useRenderIcon } from "@/components/ReIcon/src/hooks";
import { ReAdvancedSearch } from "@/components/ReAdvancedSearch";
import type { FilterItem, SelectOption } from "@/components/ReAdvancedSearch";
import DriverDialog from "./dialog.vue";

import Delete from "~icons/ep/delete";
import Edit from "~icons/ep/edit";
import View from "~icons/ep/view";
import Refresh from "~icons/ep/refresh";
import ArrowDown from "~icons/ep/arrow-down";
import Plus from "~icons/ep/plus";

defineOptions({
  name: "DriverMonitor"
});

const formRef = ref();
const tableRef = ref();
const advancedSearchRef = ref();
const driverDialogRef = ref<InstanceType<typeof DriverDialog>>();

const handleReset = () => {
  resetForm(formRef.value);
  advancedFilters.value = [];
  advancedSearchRef.value?.clearFilters();
};

const handleOpenDialog = (result: {
  mode: "add" | "edit" | "detail";
  row: any;
}) => {
  driverDialogRef.value?.open(result.mode, result.row);
};

const handleDialogSave = () => {
  onSearch();
};

const advancedFilters = ref<FilterItem[]>([]);

const {
  form,
  loading,
  columns,
  dataList,
  pagination,
  selectedNum,
  statistics,
  dailyFatigueChartRef,
  dmsTriggerChartRef,
  driverFatigueChartRef,
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
  handleSelectionChange
} = useRole(tableRef, advancedFilters);

const handleCommand = (command: string, row: any) => {
  if (command === "detail") {
    handleOpenDialog(onDetail(row));
  } else if (command === "delete") {
    onDelete(row);
  }
};

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
      <el-form-item label="司机姓名" prop="driverName">
        <el-input
          v-model="form.driverName"
          placeholder="请输入司机姓名"
          clearable
          class="w-37.5!"
        />
      </el-form-item>
      <el-form-item label="日期" prop="dateRange">
        <el-date-picker
          v-model="form.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          class="w-52!"
        />
      </el-form-item>
      <el-form-item label="驾驶员状态" prop="driverStatus">
        <el-select
          v-model="form.driverStatus"
          placeholder="请选择状态"
          clearable
          class="w-37.5!"
        >
          <el-option label="正常" value="NORMAL" />
          <el-option label="轻微疲劳" value="MILDFAIR" />
          <el-option label="疲劳" value="FATIGUE" />
          <el-option label="严重疲劳" value="SEVEREFATIGUE" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <div class="flex items-center gap-2">
          <ReAdvancedSearch
            v-if="false"
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

    <PureTableBar title="驾驶员监测" :columns="columns" @refresh="onSearch" tableKey="driverTable">
      <template #buttons>
        <div class="flex justify-end flex-1">
          <el-button
            type="primary"
            :icon="useRenderIcon(Plus)"
            @click="handleOpenDialog(onAdd())"
          >
            新增记录
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
          <template #remark="{ row }">
            <el-tooltip
              v-if="row.remark && row.remark.length > 11"
              :content="row.remark"
              placement="top"
            >
              <div class="truncate">{{ row.remark }}</div>
            </el-tooltip>
            <span v-else-if="row.remark">{{ row.remark }}</span>
            <span v-else>-</span>
          </template>
          <template #operation="{ row }">
            <div class="flex items-center justify-center gap-2">
              <el-button
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
              </el-dropdown>
            </div>
          </template>
        </pure-table>
      </template>
    </PureTableBar>

    <div class="mt-4 grid grid-cols-5 gap-4">
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          监测总数
        </div>
        <div class="text-2xl font-bold">{{ statistics.total }}</div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          正常
        </div>
        <div class="text-2xl font-bold text-[#67C23A]">
          {{ statistics.normal }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          轻微疲劳
        </div>
        <div class="text-2xl font-bold text-[#E6A23C]">
          {{ statistics.slightFatigue }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          疲劳
        </div>
        <div class="text-2xl font-bold text-[#F56C6C]">
          {{ statistics.fatigue }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          严重疲劳
        </div>
        <div class="text-2xl font-bold text-[#909399]">
          {{ statistics.severeFatigue }}
        </div>
      </div>
    </div>

    <div class="mt-4 grid grid-cols-3 gap-4 pb-4">
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-base font-medium mb-4">每日出现疲劳状态司机数</div>
        <div ref="dailyFatigueChartRef" class="h-64"></div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-base font-medium mb-4">DMS每日触发次数</div>
        <div ref="dmsTriggerChartRef" class="h-64"></div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-base font-medium mb-4">按司机维度统计疲劳次数</div>
        <div ref="driverFatigueChartRef" class="h-64"></div>
      </div>
    </div>

    <DriverDialog ref="driverDialogRef" @save="handleDialogSave" />
  </div>
</template>

<style lang="scss" scoped>
:deep(.el-dropdown-menu__item i) {
  margin: 0;
}

:deep(.el-dropdown-menu__item--divided) {
  margin-top: 1px;
  margin-bottom: 1px;
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px 16px;
}

.main-content {
  margin: 24px 24px 0 !important;
}

.search-form {
  :deep(.el-form-item) {
    margin-bottom: 12px;
  }
}
</style>
