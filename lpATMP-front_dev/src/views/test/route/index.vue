<script setup lang="ts">
import { ref } from "vue";
import { useRole } from "./hook";
import { PureTableBar } from "@/components/RePureTableBar";
import { useRenderIcon } from "@/components/ReIcon/src/hooks";
import { hasAuth } from "@/router/utils";

import Delete from "~icons/ep/delete";
import Edit from "~icons/ep/edit";
import View from "~icons/ep/view";
import Refresh from "~icons/ep/refresh";
import Plus from "~icons/ep/plus";
import ArrowDown from "~icons/ep/arrow-down";
import RouteDialog from "./dialog.vue";

defineOptions({
  name: "RouteManage"
});

const formRef = ref();
const tableRef = ref();
const routeDialogRef = ref<InstanceType<typeof RouteDialog>>();

const {
  form,
  loading,
  columns,
  dataList,
  pagination,
  selectedNum,
  onSearch,
  resetForm,
  onbatchDel,
  onDetail,
  onAdd,
  onEdit,
  onDelete,
  handleSizeChange,
  onSelectionCancel,
  handleCurrentChange,
  handleSelectionChange,
  handleSortChange
} = useRole(tableRef);

// 弹窗打开处理
const handleOpenDialog = (result: {
  mode: "add" | "edit" | "detail";
  row: any;
}) => {
  routeDialogRef.value?.open(result.mode, result.row);
};

// 弹窗保存处理
const handleDialogSave = (data: any) => {
  console.log("保存数据:", data);
  onSearch();
};

// 更多操作命令处理
const handleCommand = (command: string, row: any) => {
  if (command === "detail") {
    handleOpenDialog(onDetail(row));
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
      <el-form-item label="测试功能" prop="test_func">
        <el-input
          v-model="form.test_func"
          placeholder="请输入测试功能"
          clearable
          class="w-42.5!"
        />
      </el-form-item>
      <el-form-item label="难度系数" prop="diff">
        <el-input
          v-model="form.diff"
          placeholder="请输入难度系数"
          clearable
          class="w-42.5!"
        />
      </el-form-item>
      <el-form-item label="城市" prop="location">
        <el-input
          v-model="form.location"
          placeholder="请输入城市"
          clearable
          class="w-42.5!"
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

    <PureTableBar
      title="路线管理"
      :columns="columns"
      @refresh="onSearch"
      tableKey="routeTable"
    >
      <template #buttons>
        <div class="flex justify-end flex-1">
          <el-button
            type="primary"
            :icon="useRenderIcon(Plus)"
            @click="handleOpenDialog(onAdd())"
            v-if="hasAuth('route:add')"
          >
            新增路线
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
          @sort-change="handleSortChange"
          border
        >
          <template #routeDesc="{ row }">
            <el-tooltip
              v-if="row.routeDesc && row.routeDesc.length > 11"
              :content="row.routeDesc"
              placement="top"
              :popper-style="{ maxWidth: '300px' }"
            >
              <div class="truncate">{{ row.routeDesc }}</div>
            </el-tooltip>
            <div v-else-if="row.routeDesc">
              {{ row.routeDesc }}
            </div>
            <div v-else>-</div>
          </template>
          <template #routeFeature="{ row }">
            <el-tooltip
              v-if="row.routeFeature && row.routeFeature.length > 11"
              :content="row.routeFeature"
              placement="top"
              :popper-style="{ maxWidth: '300px' }"
            >
              <div class="truncate">{{ row.routeFeature }}</div>
            </el-tooltip>
            <div v-else-if="row.routeFeature">
              {{ row.routeFeature }}
            </div>
            <div v-else>-</div>
          </template>
          <template #remark="{ row }">
            <el-tooltip
              v-if="row.remark && row.remark.length > 11"
              :content="row.remark"
              placement="top"
              :popper-style="{ maxWidth: '300px' }"
            >
              <div class="truncate">{{ row.remark }}</div>
            </el-tooltip>
            <div v-else-if="row.remark">
              {{ row.remark }}
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
                @click="handleOpenDialog(onEdit(row))"
                v-if="hasAuth('route:edit')"
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
                    <el-dropdown-item command="delete" divided v-if="hasAuth('route:delete')">
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

    <!-- 路线弹窗 -->
    <RouteDialog ref="routeDialogRef" @save="handleDialogSave" />
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
