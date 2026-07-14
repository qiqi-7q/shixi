<script setup lang="ts">
import { ref } from "vue";
import { useRole } from "./hook";
import { PureTableBar } from "@/components/RePureTableBar";
import { useRenderIcon } from "@/components/ReIcon/src/hooks";

import Delete from "~icons/ep/delete";
import Edit from "~icons/ep/edit";
import View from "~icons/ep/view";
import Refresh from "~icons/ep/refresh";
import Plus from "~icons/ep/plus";
import ArrowDown from "~icons/ep/arrow-down";
import MileageDialog from "./dialog.vue";

defineOptions({
  name: "TestMileage"
});

const formRef = ref();
const tableRef = ref();
const mileageDialogRef = ref<InstanceType<typeof MileageDialog>>();

const {
  form,
  loading,
  columns,
  dataList,
  pagination,
  selectedNum,
  statistics,
  versionChartRef,
  dailyChartRef,
  featureChartRef,
  onSearch,
  resetForm,
  onbatchDel,
  onDetail,
  onAdd,
  onEdit,
  onSave,
  onDelete,
  handleSizeChange,
  onSelectionCancel,
  handleCurrentChange,
  handleSelectionChange
} = useRole(tableRef, mileageDialogRef);

// 更多操作命令处理
const handleCommand = (command: string, row: any) => {
  if (command === "detail") {
    onDetail(row);
  } else if (command === "delete") {
    onDelete(row);
  }
};
</script>

<template>
  <div class="main">
    <el-form
      ref="formRef"
      :inline="true"
      :model="form"
      class="search-form bg-bg_color w-full pl-8 pt-3 overflow-auto"
    >
      <el-form-item label="项目" prop="project">
        <el-input
          v-model="form.project"
          placeholder="请输入项目名称"
          clearable
          class="w-42.5!"
        />
      </el-form-item>
      <el-form-item label="测试版本" prop="version">
        <el-input
          v-model="form.version"
          placeholder="请输入测试版本"
          clearable
          class="w-42.5!"
        />
      </el-form-item>
      <el-form-item label="测试功能" prop="testFeature">
        <el-select
          v-model="form.testFeature"
          placeholder="请选择"
          clearable
          class="w-37.5!"
        >
          <el-option label="NAP" value="NAP" />
          <el-option label="CNAP" value="CNAP" />
          <el-option label="LCC/ACC" value="LCC/ACC" />
        </el-select>
      </el-form-item>
      <el-form-item label="测试时间" prop="testTime">
        <el-date-picker
          v-model="form.testTime"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          class="w-60!"
        />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          :icon="useRenderIcon('ri/search-line')"
          :loading="loading"
          @click="onSearch"
        >
          搜索
        </el-button>
        <el-button :icon="useRenderIcon(Refresh)" @click="resetForm(formRef)">
          重置
        </el-button>
      </el-form-item>
    </el-form>

    <PureTableBar title="测试里程" :columns="columns" @refresh="onSearch" tableKey="mileageTable">
      <template #buttons>
        <div class="flex justify-end flex-1">
          <el-button
            type="primary"
            :icon="useRenderIcon(Plus)"
            @click="onAdd()"
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

    <!-- 统计卡片 -->
    <div class="mt-4 grid grid-cols-4 gap-4">
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          总记录数
        </div>
        <div class="text-2xl font-bold">{{ statistics.totalRecords }}</div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          总里程(km)
        </div>
        <div class="text-2xl font-bold text-[#409EFF]">
          {{ statistics.totalMileage }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          NAP里程(km)
        </div>
        <div class="text-2xl font-bold text-[#67C23A]">
          {{ statistics.napMileage }}
        </div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-sm text-[var(--el-text-color-secondary)] mb-1">
          CNAP里程(km)
        </div>
        <div class="text-2xl font-bold text-[#E6A23C]">
          {{ statistics.cnapMileage }}
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="mt-4 grid grid-cols-3 gap-4 pb-4">
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-base font-medium mb-4">版本里程</div>
        <div ref="versionChartRef" class="h-64"></div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-base font-medium mb-4">每日里程</div>
        <div ref="dailyChartRef" class="h-64"></div>
      </div>
      <div class="bg-bg_color p-4 rounded shadow">
        <div class="text-base font-medium mb-4">功能里程</div>
        <div ref="featureChartRef" class="h-64"></div>
      </div>
    </div>

    <!-- 测试里程弹窗 -->
    <MileageDialog ref="mileageDialogRef" @save="onSave" />
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
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}
</style>
