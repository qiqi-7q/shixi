<script setup lang="ts">
import { ref } from "vue";
import { useRole } from "./hook";
import { PureTableBar } from "@/components/RePureTableBar";
import { useRenderIcon } from "@/components/ReIcon/src/hooks";
import Dialog from "./dialog.vue";
import Plus from "~icons/ep/plus";
import { hasAuth } from "@/router/utils";

import Delete from "~icons/ep/delete";
import Edit from "~icons/ep/edit";
import View from "~icons/ep/view";
import Refresh from "~icons/ep/refresh";
import ArrowDown from "~icons/ep/arrow-down";

defineOptions({
  name: "PermissionRole"
});

const formRef = ref();
const tableRef = ref();
const dialogRef = ref();
const handleOpenDialog = (result: {
  mode: "add" | "edit" | "detail";
  row: any;
}) => {
  dialogRef.value?.open(result.mode, result.row);
};
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
  onAdd,
  onEdit,
  onDetail,
  onDelete,
  handleSave,
  handleSizeChange,
  onSelectionCancel,
  handleCurrentChange,
  handleSelectionChange
} = useRole(tableRef, dialogRef);

const handleCommand = (command: string, row: any) => {
  if (command === "edit") {
    onEdit(row);
  } else if (command === "detail") {
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
      <el-form-item label="角色搜索" prop="search">
        <el-input
          v-model="form.search"
          placeholder="请输入角色名称或编码"
          clearable
          class="w-60!"
          @keyup.enter="onSearch"
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
      title="角色权限管理"
      :columns="columns"
      @refresh="onSearch"
      tableKey="roleTable"
    >
      <template #buttons>
        <div class="flex justify-end flex-1">
          <el-button
            type="primary"
            :icon="useRenderIcon(Plus)"
            @click="onAdd"
            v-if="hasAuth('role:add')"
          >
            新增角色
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
          adaptive
          :adaptiveConfig="{ offsetBottom: 108 }"
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
            <div class="flex items-center justify-center gap-2">
              <el-button
                class="reset-margin outline-hidden!"
                link
                type="primary"
                :size="size"
                :icon="useRenderIcon(Edit)"
                @click="onEdit(row)"
                v-if="hasAuth('role:update')"
              >
                编辑权限
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
                    <el-dropdown-item
                      command="detail"
                      v-if="hasAuth('role:read')"
                    >
                      <el-icon class="mr-1"
                        ><component :is="useRenderIcon(View)"
                      /></el-icon>
                      详情
                    </el-dropdown-item>
                    <el-dropdown-item
                      command="delete"
                      divided
                      v-if="hasAuth('role:delete') && row.code !== 'superuser'"
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

    <Dialog ref="dialogRef" @save="handleSave" />
  </div>
</template>
