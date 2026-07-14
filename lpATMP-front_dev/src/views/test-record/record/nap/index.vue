<script setup lang="ts">
import { ref, computed } from "vue";
import { useTestRecord } from "./hook";
import { PureTableBar } from "@/components/RePureTableBar";
import { useRenderIcon } from "@/components/ReIcon/src/hooks";
import { ReAdvancedSearch } from "@/components/ReAdvancedSearch";
import type { FilterItem, SelectOption } from "@/components/ReAdvancedSearch";
import { storageLocal } from "@pureadmin/utils";
import { userKey, type DataInfo } from "@/utils/auth";

import Delete from "~icons/ep/delete";
import Edit from "~icons/ep/edit";
import View from "~icons/ep/view";
import Refresh from "~icons/ep/refresh";
import Plus from "~icons/ep/plus";
import ArrowDown from "~icons/ep/arrow-down";
import Upload from "~icons/ep/upload";
import Download from "~icons/ep/download";
import NapDialog from "./dialog.vue";
import ImageUploadCell from "./ImageUploadCell.vue";
import { hasAuth } from "@/router/utils";

defineOptions({
  name: "TestRecordNap"
});

const currentUserId = computed(
  () => storageLocal().getItem<DataInfo<number>>(userKey)?.userid ?? ""
);

const formRef = ref();
const tableRef = ref();
const advancedSearchRef = ref();
const napDialogRef = ref<InstanceType<typeof NapDialog>>();

const advancedFilters = ref<FilterItem[]>([]);

const {
  form,
  loading,
  columns,
  dataList,
  pagination,
  selectedNum,
  importDialogVisible,
  importLoading,
  importFile,
  editMap,
  projectOptions,
  carTypeOptions,
  softwareVersionOptions,
  onSearch,
  resetForm,
  onbatchDel,
  onDetail,
  onEdit,
  onSave,
  onCancel,
  onDelete,
  onAdd,
  onImport,
  handleFileChange,
  handleFileRemove,
  handleImport,
  onExport,
  onDownloadTemplate,
  handleSizeChange,
  onSelectionCancel,
  handleCurrentChange,
  handleSelectionChange
} = useTestRecord(tableRef, advancedFilters);

const handleReset = () => {
  resetForm(formRef.value);
  advancedFilters.value = [];
  advancedSearchRef.value?.clearFilters();
  onSelectionCancel();
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
      <el-form-item label="车型" prop="car_type">
        <el-select
          v-model="form.car_type"
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
      <el-form-item label="软件版本" prop="software_version">
        <el-select
          v-model="form.software_version"
          placeholder="请选择软件版本"
          filterable
          clearable
        >
          <el-option
            v-for="s in softwareVersionOptions"
            :key="s"
            :label="s"
            :value="s"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="功能模式" prop="function_mode">
        <el-select
          v-model="form.function_mode"
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
      title="测试记录列表"
      :columns="columns"
      tableKey="nap-record"
      @refresh="onSearch"
    >
      <template #buttons>
        <div class="flex justify-end flex-1 gap-2">
          <el-button
            type="success"
            :icon="useRenderIcon(Upload)"
            @click="onImport"
            v-if="hasAuth('test_record:import')"
          >
            批量导入
          </el-button>
          <el-button
            type="warning"
            :icon="useRenderIcon(Download)"
            @click="onExport"
            v-if="hasAuth('test_record:export')"
          >
            批量导出
          </el-button>
          <el-button
            type="primary"
            :icon="useRenderIcon(Plus)"
            @click="onAdd"
            v-if="hasAuth('test_record:add')"
          >
            新建问题
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
            <el-button type="primary" link @click="onSelectionCancel">
              取消选择
            </el-button>
          </div>
          <!-- <el-popconfirm title="是否确认删除?" @confirm="onbatchDel">
            <template #reference>
              <el-button type="danger" link class="mr-1!"> 批量删除 </el-button>
            </template>
          </el-popconfirm> -->
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
          tableKey="nap-record"
          border
        >
          <template #remarks="{ row }">
            <el-tooltip
              v-if="row.remarks && row.remarks.length > 10"
              :content="row.remarks"
              placement="top"
              :popper-style="{ maxWidth: '300px' }"
            >
              <div>{{ row.remarks }}</div>
            </el-tooltip>
            <div v-else-if="row.remarks">
              {{ row.remarks }}
            </div>
            <div v-else>-</div>
          </template>
          <template #data_link="{ row }">
            <el-link
              v-if="row.data_link"
              type="primary"
              underline="never"
              :href="row.data_link"
              target="_blank"
              class="text-sm"
            >
              {{ row.data_link }}
            </el-link>
            <span v-else class="text-gray-400">-</span>
          </template>
          <template #wetrack_link="{ row }">
            <el-link
              v-if="row.wetrack_link"
              type="primary"
              underline="never"
              :href="row.wetrack_link"
              target="_blank"
              class="text-sm"
            >
              {{ row.wetrack_link }}
            </el-link>
            <span v-else class="text-gray-400">-</span>
          </template>
          <template #analyze_attach="{ row, $index }">
            <ImageUploadCell
              style="width: 150px"
              :row="row"
              :editRow="editMap[$index]"
              :editable="!!editMap[$index]?.editable"
              @update="
                images => {
                  if (editMap[$index]) editMap[$index].analyze_attach = images;
                }
              "
            />
          </template>
          <template #problem_desc="{ row }">
            <el-tooltip
              v-if="row.problem_desc && row.problem_desc.length > 10"
              :content="row.problem_desc"
              placement="top"
              :popper-style="{ maxWidth: '300px' }"
            >
              <div class="truncate">{{ row.problem_desc }}</div>
            </el-tooltip>
            <span v-else-if="row.problem_desc">{{ row.problem_desc }}</span>
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
          <template #operation="{ row, index }">
            <div
              class="operation-container flex items-center justify-center gap-2"
            >
              <template v-if="hasAuth('test_record:update')">
                <el-button
                  v-if="!editMap[index]?.editable"
                  class="reset-margin outline-hidden!"
                  link
                  :type="row.creator_id == currentUserId ? 'primary' : 'text'"
                  :size="size"
                  :icon="useRenderIcon(Edit)"
                  :disabled="row.creator_id != currentUserId"
                  @click="onEdit(row, index)"
                >
                  编辑
                </el-button>
                <div v-else class="flex items-center gap-2">
                  <el-button
                    class="reset-margin outline-hidden!"
                    link
                    type="primary"
                    :size="size"
                    @click="onSave(index)"
                  >
                    保存
                  </el-button>
                  <el-button
                    class="reset-margin outline-hidden!"
                    link
                    :size="size"
                    @click="onCancel(index)"
                  >
                    取消
                  </el-button>
                </div>
              </template>
              <el-dropdown
                v-if="!editMap[index]?.editable"
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
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </pure-table>
      </template>
    </PureTableBar>

    <NapDialog ref="napDialogRef" @save="handleDialogSave" />

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
          <span class="text-lg font-medium">批量导入Excel数据</span>
          <el-link
            type="primary"
            underline="never"
            @click="onDownloadTemplate"
            class="text-sm ml-1"
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
          accept=".xlsx"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
        >
          <div class="el-upload__text">
            将Excel文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">仅支持 .xlsx 格式的Excel文件</div>
          </template>
        </el-upload>
        <div v-else class="flex items-center gap-2 p-3 bg-gray-50 rounded">
          <el-icon class="text-green-500"
            ><component :is="useRenderIcon('ep/document')"
          /></el-icon>
          <span class="flex-1 truncate">{{ importFile.name }}</span>
          <el-button type="danger" link size="small" @click="handleFileRemove">
            移除
          </el-button>
        </div>
        <el-alert
          class="mt-4"
          title="说明：上传Excel文件后，系统将自动读取并导入数据。导入过程中会自动进行数据去重和格式校验。"
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
</style>
