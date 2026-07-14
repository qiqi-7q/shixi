<script setup lang="ts">
import { ref, computed } from "vue";
import { useRole } from "./hook";
import { PureTableBar } from "@/components/RePureTableBar";
import { useRenderIcon } from "@/components/ReIcon/src/hooks";
import { ReAdvancedSearch } from "@/components/ReAdvancedSearch";
import type { FilterItem, SelectOption } from "@/components/ReAdvancedSearch";

import Delete from "~icons/ep/delete";
import Edit from "~icons/ep/edit";
import View from "~icons/ep/view";
import Refresh from "~icons/ep/refresh";
import Plus from "~icons/ep/plus";
import ArrowDown from "~icons/ep/arrow-down";
import TaskDialog from "./dialog.vue";

defineOptions({
  name: "TestTask"
});

const formRef = ref();
const tableRef = ref();
const advancedSearchRef = ref();
const taskDialogRef = ref<InstanceType<typeof TaskDialog>>();

const handleReset = () => {
  resetForm(formRef.value);
  advancedFilters.value = [];
  advancedSearchRef.value?.clearFilters();
};

const handleOpenDialog = (result: {
  mode: "add" | "edit" | "detail";
  row: any;
}) => {
  taskDialogRef.value?.open(result.mode, result.row);
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
  dailyChartRef,
  statusChartRef,
  featureChartRef,
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
      :model="form"
      class="search-form bg-bg_color w-full pl-8 pt-3 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-x-4"
    >
      <el-form-item label="项目" prop="project">
        <el-input
          v-model="form.project"
          placeholder="请输入项目名称"
          clearable
        />
      </el-form-item>
      <el-form-item label="测试时间" prop="testTimeRange">
        <el-date-picker
          v-model="form.testTimeRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item label="测试功能" prop="testFeature">
        <el-select v-model="form.testFeature" placeholder="请选择" clearable>
          <el-option label="NAP" value="NAP" />
          <el-option label="CNAP" value="CNAP" />
          <el-option label="LCC/ACC" value="LCC/ACC" />
        </el-select>
      </el-form-item>
      <el-form-item label="任务发布人" prop="publisher">
        <el-input
          v-model="form.publisher"
          placeholder="请输入发布人"
          clearable
        />
      </el-form-item>
      <el-form-item label="测试人员" prop="tester">
        <el-input
          v-model="form.tester"
          placeholder="请输入测试人员"
          clearable
        />
      </el-form-item>
      <el-form-item label="任务状态" prop="taskStatus">
        <el-select v-model="form.taskStatus" placeholder="请选择状态" clearable>
          <el-option label="完成" value="完成" />
          <el-option label="进行中" value="进行中" />
          <el-option label="未开始" value="未开始" />
          <el-option label="未达标" value="未达标" />
          <el-option label="挂起" value="挂起" />
        </el-select>
      </el-form-item>
      <el-form-item label="是否用于KPI统计" prop="is_kpi">
        <el-select v-model="form.is_kpi" placeholder="请选择" clearable>
          <el-option label="是" :value="true" />
          <el-option label="否" :value="false" />
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

    <PureTableBar title="任务管理" :columns="columns" @refresh="onSearch" tableKey="taskTable">
      <template #buttons>
        <div class="flex justify-end flex-1">
          <el-button
            type="primary"
            :icon="useRenderIcon(Plus)"
            @click="handleOpenDialog(onAdd())"
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
          <template #task_desc="{ row }">
            <el-tooltip
              v-if="row.task_desc && row.task_desc.length > 10"
              :content="row.task_desc"
              placement="top"
              :popper-style="{ maxWidth: '300px' }"
            >
              <div class="truncate">{{ row.task_desc }}</div>
            </el-tooltip>
            <span v-else-if="row.task_desc">{{ row.task_desc }}</span>
            <span v-else>-</span>
          </template>
          <template #reason_desc="{ row }">
            <el-tooltip
              v-if="row.reason_desc && row.reason_desc.length > 10"
              :content="row.reason_desc"
              placement="top"
              :popper-style="{ maxWidth: '300px' }"
            >
              <div class="truncate">{{ row.reason_desc }}</div>
            </el-tooltip>
            <div v-else-if="row.reason_desc" class="truncate">
              {{ row.reason_desc }}
            </div>
            <div v-else class="truncate">-</div>
          </template>
          <template #remarks="{ row }">
            <el-tooltip
              v-if="row.remarks && row.remarks.length > 10"
              :content="row.remarks"
              placement="top"
              :popper-style="{ maxWidth: '300px' }"
            >
              <div class="truncate">{{ row.remarks }}</div>
            </el-tooltip>
            <div v-else-if="row.remarks" class="truncate">
              {{ row.remarks }}
            </div>
            <div v-else class="truncate">-</div>
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

    <div class="mt-4 grid grid-cols-6 gap-4">
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          任务总数
        </div>
        <div class="text-2xl font-bold">{{ statistics.total }}</div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          完成
        </div>
        <div class="text-2xl font-bold text-[#67C23A]">
          {{ statistics.completed }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          进行中
        </div>
        <div class="text-2xl font-bold text-[#409EFF]">
          {{ statistics.inProgress }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          未开始
        </div>
        <div class="text-2xl font-bold text-[#909399]">
          {{ statistics.notStarted }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          未达标
        </div>
        <div class="text-2xl font-bold text-[#F56C6C]">
          {{ statistics.notQualified }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          挂起
        </div>
        <div class="text-2xl font-bold text-[#FF9900]">
          {{ statistics.pending }}
        </div>
      </div>
    </div>

    <div class="mt-4 grid grid-cols-3 gap-4 pb-4">
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-base font-medium mb-4">每日任务下发量</div>
        <div ref="dailyChartRef" class="h-64"></div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-base font-medium mb-4">任务状态</div>
        <div ref="statusChartRef" class="h-64"></div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-base font-medium mb-4">各个功能任务量</div>
        <div ref="featureChartRef" class="h-64"></div>
      </div>
    </div>

    <TaskDialog ref="taskDialogRef" @save="handleDialogSave" />
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
  padding-right: 32px;

  :deep(.el-form-item) {
    margin-bottom: 12px;
  }

  :deep(.el-form-item__content) {
    width: 100%;
  }

  :deep(.el-input),
  :deep(.el-select),
  :deep(.el-date-editor) {
    width: 100% !important;
  }
}
:deep(.el-table__header th .cell) {
  white-space: nowrap !important;
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: keep-all;
}
:deep(.no-wrap-cell) {
  white-space: nowrap; /* 禁止换行 */
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
