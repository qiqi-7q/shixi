<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { message } from "@/utils/message";
import { ElMessageBox } from "element-plus";
import Plus from "~icons/ep/plus";
import Delete from "~icons/ep/delete";
import Edit from "~icons/ep/edit";
import {
  getAbellList,
  getLabelAll,
  getLabelField,
  saveAbellList,
  deleteAbellList
} from "@/api/system";
import { hasAuth } from "@/router/utils";

defineOptions({
  name: "DictManage"
});

interface FieldItem {
  field: string;
  field_cn?: string;
  labels: string[];
}

interface ModuleData {
  name: string;
  label?: string;
  fields: FieldItem[];
}

const activeModule = ref("");
const activeField = ref<Record<string, string>>({});
const modules = ref<ModuleData[]>([]);
const loading = ref(false);

// 标签编辑弹窗
const dialogVisible = ref(false);
const dialogTitle = ref("");
const currentModule = ref("");
const currentField = ref("");
const editLabels = ref<string[]>([]);
const newLabelValue = ref("");

// 新建标签弹窗
const addDialogVisible = ref(false);

// 新增模块弹窗
const moduleDialogVisible = ref(false);
const newModuleName = ref("");
const newModuleField = ref("");

// 新增字段弹窗
const fieldDialogVisible = ref(false);
const newFieldModule = ref("");

// 可用字段（从 getLabelAll 获取）
const allTableFields = ref<Record<string, string>>({});
const moduleFieldOptions = ref<{ label: string; value: string }[]>([]);
const fieldOptions = ref<{ label: string; value: string }[]>([]);

// 监听模块名输入变化，更新模块弹窗的字段选项
watch(newModuleName, async name => {
  const trimmed = name.trim();
  if (!trimmed) {
    moduleFieldOptions.value = [];
    newModuleField.value = "";
    return;
  }
  try {
    const res: any = await getLabelField(trimmed);
    if (res && typeof res === "object") {
      moduleFieldOptions.value = Object.entries(res).map(([key, comment]) => ({
        label: `${key}（${comment}）`,
        value: key
      }));
    } else {
      moduleFieldOptions.value = [];
    }
  } catch {
    moduleFieldOptions.value = [];
  }
  newModuleField.value = "";
});

// 根据外层模块获取字段选项
async function fetchFieldOptions() {
  const tableName = activeModule.value;
  if (!tableName) {
    fieldOptions.value = [];
    return;
  }
  try {
    const res: any = await getLabelField(tableName);
    if (res && typeof res === "object") {
      fieldOptions.value = Object.entries(res).map(([key, comment]) => ({
        label: `${key}（${comment}）`,
        value: key
      }));
    } else {
      fieldOptions.value = [];
    }
  } catch {
    fieldOptions.value = [];
  }
  newFieldModule.value = "";
}

// 加载全部模块标签
async function loadAllModules() {
  loading.value = true;
  try {
    const allRes: any = await getLabelAll();
    // getLabelAll 返回 { table_name: comment }
    if (allRes && typeof allRes === "object") {
      allTableFields.value = allRes;
      modules.value = Object.entries(allRes).map(([name, label]) => ({
        name,
        label: label as string,
        fields: []
      }));
    }
    // 默认选中第一个模块并加载其字段
    if (modules.value.length > 0) {
      const defaultModule = modules.value[0].name;
      activeModule.value = defaultModule;
      await loadModuleFields(defaultModule);
    }
  } catch (e) {
    message("加载标签数据失败", { type: "error" });
  } finally {
    loading.value = false;
  }
}

// 加载指定模块的字段
async function loadModuleFields(moduleName: string) {
  try {
    const res: any = await getAbellList({ module_name: moduleName });
    const mod = modules.value.find(m => m.name === moduleName);
    if (!mod) return;
    if (res?.data && Array.isArray(res.data)) {
      mod.fields = res.data.map((item: any) => ({
        field: item.field,
        field_cn: item.field_cn,
        labels: item.labels || []
      }));
      if (mod.fields.length > 0) {
        activeField.value[moduleName] = mod.fields[0].field;
      }
    } else {
      mod.fields = [];
    }
  } catch {
    // ignore
  }
}

// 选择模块
function selectModule(name: string) {
  activeModule.value = name;
  loadModuleFields(name);
}

function getCurrentModule(): ModuleData | undefined {
  return modules.value.find(m => m.name === activeModule.value);
}

// 新增模块
function addModule() {
  newModuleName.value = "";
  newModuleField.value = "";
  moduleDialogVisible.value = true;
}

async function saveModule() {
  const name = newModuleName.value.trim();
  const fieldName = newModuleField.value.trim();
  if (!name) {
    message("请输入模块名", { type: "warning" });
    return;
  }
  if (!fieldName) {
    message("请输入字段名", { type: "warning" });
    return;
  }
  if (modules.value.some(m => m.name === name)) {
    message("模块已存在", { type: "warning" });
    return;
  }
  try {
    await saveAbellList({
      module_name: name,
      field_name: fieldName,
      labels: []
    });
    modules.value.push({ name, fields: [{ field: fieldName, labels: [] }] });
    activeField.value[name] = fieldName;
    moduleDialogVisible.value = false;
    if (!activeModule.value) {
      activeModule.value = name;
    }
    message("新增模块成功", { type: "success" });
  } catch (e: any) {
    const msg = e?.response?.data?.message || "新增模块失败";
    message(msg, { type: "error" });
  }
}

// 删除模块
async function deleteModule(name: string) {
  try {
    await ElMessageBox.confirm(
      `确认要删除模块"${name}"及其所有标签吗？`,
      "系统提示",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      }
    );
    await deleteAbellList({ module_name: name });
    modules.value = modules.value.filter(m => m.name !== name);
    if (activeModule.value === name) {
      activeModule.value = modules.value[0]?.name || "";
    }
    message("删除成功", { type: "success" });
  } catch {
    // 取消
  }
}

// 新增字段
function addField() {
  newFieldModule.value = "";
  fieldDialogVisible.value = true;
  fetchFieldOptions();
}

async function saveField() {
  const moduleName = activeModule.value;
  const fieldName = newFieldModule.value;
  if (!fieldName) {
    message("请选择字段", { type: "warning" });
    return;
  }
  const mod = modules.value.find(m => m.name === moduleName);
  if (!mod) {
    // 模块不存在，创建新模块
    try {
      await saveAbellList({
        module_name: moduleName,
        field_name: fieldName,
        labels: []
      });
      modules.value.push({
        name: moduleName,
        fields: [{ field: fieldName, field_cn: "", labels: [] }]
      });
      activeField.value[moduleName] = fieldName;
      if (!activeModule.value) {
        activeModule.value = moduleName;
      }
      fieldDialogVisible.value = false;
      message("新增字段成功", { type: "success" });
    } catch (e: any) {
      const msg = e?.response?.data?.message || "新增字段失败";
      message(msg, { type: "error" });
    }
    return;
  }
  if (mod.fields.some(f => f.field === fieldName)) {
    message("字段已存在", { type: "warning" });
    return;
  }
  try {
    await saveAbellList({
      module_name: moduleName,
      field_name: fieldName,
      labels: []
    });
    await loadModuleFields(moduleName);
    fieldDialogVisible.value = false;
    message("新增字段成功", { type: "success" });
  } catch (e: any) {
    const msg = e?.response?.data?.message || "新增字段失败";
    message(msg, { type: "error" });
  }
}

// 删除单个标签
async function deleteLabel(field: FieldItem, label: string) {
  try {
    await ElMessageBox.confirm(`确认要删除标签"${label}"吗？`, "删除确认", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    const newLabels = field.labels.filter(l => l !== label);
    await saveAbellList({
      module_name: activeModule.value,
      field_name: field.field,
      labels: newLabels
    });
    field.labels = newLabels;
    message("删除成功", { type: "success" });
  } catch {
    // 取消
  }
}

// 删除字段
async function deleteField(fieldName: string) {
  try {
    await ElMessageBox.confirm(`确认要删除字段"${fieldName}"吗？`, "删除确认", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    await deleteAbellList({
      module_name: activeModule.value,
      field_name: fieldName
    });
    const mod = getCurrentModule();
    if (mod) {
      mod.fields = mod.fields.filter(f => f.field !== fieldName);
      if (activeField.value[activeModule.value] === fieldName) {
        activeField.value[activeModule.value] = mod.fields[0]?.field || "";
      }
    }
    message("删除成功", { type: "success" });
  } catch {
    // 取消
  }
}

// 新建标签
function addLabelDialog(field: FieldItem) {
  currentModule.value = activeModule.value;
  currentField.value = field.field;
  newLabelValue.value = "";
  addDialogVisible.value = true;
}

async function saveNewLabel() {
  const val = newLabelValue.value.trim();
  if (!val) return;
  const mod = modules.value.find(m => m.name === currentModule.value);
  const field = mod?.fields.find(f => f.field === currentField.value);
  const allLabels = field ? [...field.labels, val] : [val];
  try {
    await saveAbellList({
      module_name: currentModule.value,
      field_name: currentField.value,
      labels: allLabels
    });
    if (field && !field.labels.includes(val)) {
      field.labels.push(val);
    }
    message("保存成功", { type: "success" });
    addDialogVisible.value = false;
  } catch (e: any) {
    const msg = e?.response?.data?.message || "保存失败";
    message(msg, { type: "error" });
  }
}

// 编辑标签
function editLabelsDialog(field: FieldItem) {
  dialogTitle.value = `编辑标签 - ${field.field}`;
  currentModule.value = activeModule.value;
  currentField.value = field.field;
  editLabels.value = [...field.labels];
  dialogVisible.value = true;
}

function removeLabel(index: number) {
  editLabels.value.splice(index, 1);
}

async function saveLabels() {
  try {
    await saveAbellList({
      module_name: currentModule.value,
      field_name: currentField.value,
      labels: editLabels.value
    });
    // 更新本地数据
    const mod = modules.value.find(m => m.name === currentModule.value);
    if (mod) {
      const field = mod.fields.find(f => f.field === currentField.value);
      if (field) {
        field.labels = [...editLabels.value];
      }
    }
    message("保存成功", { type: "success" });
    dialogVisible.value = false;
  } catch (e: any) {
    const msg = e?.response?.data?.message || "保存失败";
    message(msg, { type: "error" });
  }
}

onMounted(async () => {
  await loadAllModules();
  if (modules.value.length > 0) {
    activeModule.value = modules.value[0].name;
  }
});
</script>

<template>
  <div class="dict-manage-container">
    <el-card shadow="never">
      <el-button
        type="primary"
        :icon="Plus"
        size="small"
        @click="addModule"
        v-if="hasAuth('dict:add')"
      >
        新建模块
      </el-button>
      <div class="tabs-wrapper" style="margin-top: 12px">
        <el-tabs
          v-model="activeModule"
          @tab-click="(tab: any) => selectModule(tab.props.name)"
          tab-position="left"
          class="dict-tabs-outer"
        >
          <el-tab-pane
            v-for="mod in modules"
            :key="mod.name"
            :label="mod.label || mod.name"
            :name="mod.name"
          >
            <div v-loading="loading" class="dict-items-content">
              <div class="items-header">
                <span class="items-title"
                  >字段列表（{{ mod.fields.length }}个）</span
                >
                <div class="header-actions">
                  <el-button
                    type="primary"
                    :icon="Plus"
                    size="small"
                    @click="addField"
                  >
                    新增字段
                  </el-button>
                  <!-- <el-button
                    type="danger"
                    :icon="Delete"
                    size="small"
                    plain
                    @click="deleteModule(mod.name)"
                  >
                    删除模块
                  </el-button> -->
                </div>
              </div>

              <el-tabs
                v-model="activeField[mod.name]"
                type="border-card"
                class="dict-tabs-inner"
              >
                <el-tab-pane
                  v-for="field in mod.fields"
                  :key="field.field"
                  :label="field.field_cn || field.field"
                  :name="field.field"
                >
                  <div class="field-content">
                    <div class="field-toolbar">
                      <el-button
                        type="primary"
                        :icon="Plus"
                        size="small"
                        @click="addLabelDialog(field)"
                      >
                        新建标签
                      </el-button>
                    </div>
                    <el-table
                      :data="field.labels as any"
                      border
                      size="small"
                      style="width: 100%"
                      max-height="400"
                    >
                      <el-table-column
                        type="index"
                        label="序号"
                        width="60"
                        align="center"
                      />
                      <el-table-column prop="value" label="标签值">
                        <template #default="{ row }">
                          <el-tag size="small">{{ row as any }}</el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column label="操作" width="180" align="center">
                        <template #default="{ row }">
                          <el-button
                            type="primary"
                            :icon="Edit"
                            size="small"
                            link
                            @click="editLabelsDialog(field)"
                          >
                            编辑标签
                          </el-button>
                          <el-button
                            type="danger"
                            :icon="Delete"
                            size="small"
                            link
                            @click="deleteLabel(field, row as any)"
                          >
                            删除标签
                          </el-button>
                        </template>
                      </el-table-column>
                      <template #empty>
                        <el-empty description="暂无标签" :image-size="60" />
                      </template>
                    </el-table>
                  </div>
                </el-tab-pane>

                <el-empty
                  v-if="mod.fields.length === 0"
                  description="暂无字段，请点击新增字段"
                  :image-size="80"
                />
              </el-tabs>
            </div>
          </el-tab-pane>

          <el-empty
            v-if="modules.length === 0"
            description="暂无模块，请点击新建模块"
            :image-size="100"
            style="padding: 60px 0"
          />
        </el-tabs>
      </div>
    </el-card>

    <!-- 新建标签弹窗 -->
    <el-dialog
      v-model="addDialogVisible"
      title="新建标签"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form label-width="80px">
        <el-form-item label="标签值">
          <el-input
            v-model="newLabelValue"
            placeholder="请输入标签值"
            clearable
            @keyup.enter="saveNewLabel"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNewLabel">保存</el-button>
      </template>
    </el-dialog>

    <!-- 编辑标签弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="550px"
      :close-on-click-modal="false"
    >
      <div class="label-edit-area">
        <div class="label-list-section">
          <div class="section-label">标签列表</div>
          <div class="label-list">
            <div
              v-for="(label, idx) in editLabels"
              :key="idx"
              class="label-item"
            >
              <el-input
                v-model="editLabels[idx]"
                size="small"
                style="flex: 1"
              />
              <el-button
                type="danger"
                :icon="Delete"
                size="small"
                link
                @click="removeLabel(idx)"
              />
            </div>
            <el-empty
              v-if="editLabels.length === 0"
              description="暂无标签"
              :image-size="60"
            />
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveLabels">保存</el-button>
      </template>
    </el-dialog>

    <!-- 新增模块弹窗 -->
    <el-dialog
      v-model="moduleDialogVisible"
      title="新增模块"
      width="450px"
      :close-on-click-modal="false"
    >
      <el-form label-width="80px">
        <el-form-item label="字段名">
          <el-select
            v-model="newModuleField"
            placeholder="请先输入模块名"
            filterable
            style="width: 100%"
            :disabled="!newModuleName.trim()"
          >
            <el-option
              v-for="opt in moduleFieldOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="模块名">
          <el-input
            v-model="newModuleName"
            placeholder="请输入模块名（对应数据表名）"
            clearable
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="moduleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveModule">确定</el-button>
      </template>
    </el-dialog>

    <!-- 新增字段弹窗 -->
    <el-dialog
      v-model="fieldDialogVisible"
      title="新增字段"
      width="450px"
      :close-on-click-modal="false"
    >
      <el-form label-width="80px">
        <el-form-item label="字段名">
          <el-select
            v-model="newFieldModule"
            placeholder="请选择字段"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="opt in fieldOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="fieldDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveField">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.dict-manage-container {
  padding: 24px;
  height: 100%;
  background: #f5f7fa;
}

.dict-tabs-outer {
  :deep(.el-tabs__header) {
    margin-right: 16px;
    min-width: 140px;
  }
}

.dict-tabs-inner {
  :deep(.el-tabs__header) {
    margin-bottom: 0;
  }
}

.dict-items-content {
  padding: 0 8px;

  .items-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;

    .items-title {
      font-size: 14px;
      color: #606266;
    }

    .header-actions {
      display: flex;
      gap: 8px;
    }
  }

  .field-content {
    padding: 8px 0;

    .field-toolbar {
      display: flex;
      align-items: center;
      flex-direction: row-reverse;
      margin-bottom: 8px;
    }
  }
}

.label-edit-area {
  .label-input-row {
    display: flex;
    margin-bottom: 16px;
  }

  .label-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    min-height: 60px;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 6px;

    .label-item {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
}
</style>
