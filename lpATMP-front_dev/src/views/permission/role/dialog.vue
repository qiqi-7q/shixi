<script setup lang="ts">
import { ref, reactive, watch, onMounted, computed } from "vue";
import { message } from "@/utils/message";
import {
  createAuthRole,
  updateAuthRole,
  getAuthPermissions,
  getAuthPlatforms
} from "@/api/system";
import { useUserStoreHook } from "@/store/modules/user";
import type { FormInstance, FormRules } from "element-plus";

defineOptions({
  name: "RoleDialog"
});

const props = defineProps({
  row: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(["save"]);

const dialogVisible = ref(false);
const currentMode = ref<"add" | "edit" | "detail">("add");
const currentRow = ref<any>({});
const formRef = ref<FormInstance>();
const loading = ref(false);
const permissionLoading = ref(false);

const form = reactive({
  code: "",
  name: "",
  description: "",
  level: 1,
  platform_uuid: "",
  permission_ids: [] as number[]
});

const rules: FormRules = {
  code: [{ required: true, message: "请输入角色编码", trigger: "blur" }],
  name: [{ required: true, message: "请输入角色名称", trigger: "blur" }]
};

// 权限树数据
interface PermissionNode {
  code: string;
  label: string;
  children?: PermissionNode[];
}

const permissionTree = ref<PermissionNode[]>([]);
const checkedKeys = ref<string[]>([]);

// 详情模式下只展示已拥有的权限
const displayTree = computed(() => {
  if (currentMode.value !== "detail") return permissionTree.value;
  const checkedSet = new Set(checkedKeys.value);
  function filter(nodes: PermissionNode[]): PermissionNode[] {
    return nodes
      .map(node => {
        if (node.children) {
          const filtered = filter(node.children);
          if (filtered.length > 0) {
            return { ...node, children: filtered };
          }
        }
        if (checkedSet.has(node.code)) return { ...node };
        return null;
      })
      .filter(Boolean) as PermissionNode[];
  }
  return filter(permissionTree.value);
});
const defaultExpandAll = ref(true);

// 平台列表
const platformList = ref<any[]>([]);

// 根据等级生成唯一 code
function generateCode(level: number): string {
  const prefixMap: Record<number, string> = {
    100: "superuser",
    50: "admin",
    1: "user"
  };
  const prefix = prefixMap[level] || "user";
  const chars = "abcdefghijklmnopqrstuvwxyz0123456789";
  let random = "";
  for (let i = 0; i < 12; i++) {
    random += chars[Math.floor(Math.random() * chars.length)];
  }
  return `${prefix}_${random}`;
}

// code → id 映射，提交时用
const codeToIdMap = ref<Record<string, number>>({});

// 将 API 返回的按模块分组的权限数据转为树形结构
function buildPermissionTree(data: Record<string, any[]>): PermissionNode[] {
  const moduleLabels: Record<string, string> = {
    user: "用户管理",
    role: "角色管理",
    vehicle: "车辆资源表",
    device: "设备管理",
    task: "任务管理",
    record: "记录管理",
    dict: "字典管理",
    system: "系统管理",
    permission: "权限管理",
    platform: "平台管理",
    borrow: "车辆借用表",
    statistics: "统计分析",
    test_record: "测试记录管理",
    employer: "人员管理"
  };
  const tree: PermissionNode[] = [];
  const map: Record<string, number> = {};
  for (const [module, perms] of Object.entries(data)) {
    if (!perms || perms.length === 0) continue;
    const node: PermissionNode = {
      code: module,
      label: moduleLabels[module] || module,
      children: perms.map((p: any) => {
        map[p.code] = p.id;
        return {
          code: p.code,
          label: `${p.name} (${p.code})`
        };
      })
    };
    tree.push(node);
  }
  codeToIdMap.value = map;
  return tree;
}

async function loadPermissions() {
  permissionLoading.value = true;
  try {
    const res: any = await getAuthPermissions({ platform: "platform_a" });
    if (res.data) {
      permissionTree.value = buildPermissionTree(res.data);
    }
  } catch (e) {
    message("获取权限列表失败", { type: "error" });
  } finally {
    permissionLoading.value = false;
  }
}

async function loadPlatforms() {
  try {
    const res: any = await getAuthPlatforms();
    if (res.data && Array.isArray(res.data)) {
      platformList.value = res.data;
    }
  } catch {
    // 静默失败
  }
}

function open(mode: "add" | "edit" | "detail", row: any) {
  dialogVisible.value = true;
  currentMode.value = mode;
  currentRow.value = row || {};
  resetForm();
  if ((mode === "edit" || mode === "detail") && row) {
    form.code = row.code || "";
    form.name = row.name || "";
    form.description = row.description || "";
    form.level = row.level ?? 1;
    form.platform_uuid = row.platform_uuid || "";
    // 从 permissions 数组中提取 code
    if (row.permissions && Array.isArray(row.permissions)) {
      checkedKeys.value = row.permissions.map((p: any) => p.code || p);
    } else {
      checkedKeys.value = [];
    }
  } else if (mode === "add") {
    checkedKeys.value = [];
    // 新增时自动填入当前用户所属平台
    form.platform_uuid =
      useUserStoreHook().platform_uuid ||
      "dec2fe4f-02a1-4482-8a3d-499aafb494c4" ||
      "";
    form.code = generateCode(form.level);
  } else {
    checkedKeys.value = [];
  }
}

function resetForm() {
  form.code = "";
  form.name = "";
  form.description = "";
  form.level = 1;
  form.platform_uuid = "";
  form.permission_ids = [];
  checkedKeys.value = [];
  formRef.value?.resetFields();
}

function handleClose() {
  dialogVisible.value = false;
  resetForm();
}

async function handleSubmit() {
  if (!formRef.value) return;
  await formRef.value.validate(async valid => {
    if (!valid) return;
    loading.value = true;
    try {
      const rawChecked = Array.isArray(checkedKeys.value)
        ? checkedKeys.value
        : [];
      form.permission_ids = rawChecked
        .filter(c => codeToIdMap.value[c] !== undefined)
        .map(c => codeToIdMap.value[c]);
      if (currentMode.value === "add") {
        await createAuthRole({
          code: form.code,
          name: form.name,
          description: form.description,
          permission_ids: form.permission_ids,
          platform_uuid: form.platform_uuid,
          level: form.level
        });
        message("创建角色成功", { type: "success" });
      } else {
        await updateAuthRole(currentRow.value.id, {
          code: form.code,
          name: form.name,
          description: form.description,
          permission_ids: form.permission_ids,
          platform_uuid: form.platform_uuid,
          level: form.level
        });
        message("更新角色成功", { type: "success" });
      }
      emit("save");
      handleClose();
    } catch (e: any) {
      const msg = e?.response?.data?.detail || e?.message || "操作失败";
      message(msg, { type: "error" });
    } finally {
      loading.value = false;
    }
  });
}

function handleCheckChange(_data: any, info: any) {
  if (info && Array.isArray(info.checkedKeys)) {
    checkedKeys.value = info.checkedKeys;
  }
}

onMounted(() => {
  loadPermissions();
  loadPlatforms();
});

// 新增模式下切换等级时重新生成 code
watch(
  () => form.level,
  val => {
    if (currentMode.value === "add") {
      form.code = generateCode(val);
    }
  }
);

defineExpose({ open });
</script>

<template>
  <el-dialog
    :model-value="dialogVisible"
    :title="
      currentMode === 'add'
        ? '新增角色'
        : currentMode === 'detail'
          ? '角色详情'
          : '编辑角色'
    "
    width="650px"
    :close-on-click-modal="false"
    @close="handleClose"
    destroy-on-close
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-row :gutter="20">
        <!-- <el-col :span="12">
          <el-form-item label="角色编码" prop="code">
            <el-input
              v-model="form.code"
              placeholder="请输入角色编码"
              :disabled="currentMode === 'edit'"
            />
          </el-form-item>
        </el-col> -->
        <el-col :span="12">
          <el-form-item label="等级" prop="level">
            <el-select
              v-model="form.level"
              placeholder="请选择等级"
              :disabled="currentMode === 'detail'"
            >
              <el-option label="超级管理员" :value="100" />
              <el-option label="管理员" :value="50" />
              <el-option label="普通用户" :value="1" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="角色名称" prop="name">
            <el-input
              v-model="form.name"
              placeholder="请输入角色名称"
              :disabled="currentMode === 'detail'"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="2"
          placeholder="请输入角色描述"
          :disabled="currentMode === 'detail'"
        />
      </el-form-item>
      <el-form-item
        v-if="currentMode === 'add'"
        label="所属平台"
        prop="platform_uuid"
        :rules="[{ required: true, message: '请选择平台', trigger: 'change' }]"
      >
        <el-select
          v-model="form.platform_uuid"
          placeholder="请选择平台"
          style="width: 100%"
        >
          <el-option
            v-for="p in platformList"
            :key="p.uuid"
            :label="p.name || p.uuid"
            :value="p.uuid"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="权限配置">
        <div v-loading="permissionLoading" class="permission-tree-wrapper">
          <el-tree
            ref="treeRef"
            :data="displayTree"
            :show-checkbox="currentMode !== 'detail'"
            node-key="code"
            :default-checked-keys="checkedKeys"
            :default-expand-all="defaultExpandAll"
            :check-strictly="false"
            @check="handleCheckChange"
          >
            <template #default="{ node, data }">
              <span class="tree-node">
                <span class="tree-node-label">{{ data.label }}</span>
              </span>
            </template>
          </el-tree>
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <template v-if="currentMode === 'detail'">
        <el-button @click="handleClose">关闭</el-button>
      </template>
      <template v-else>
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </template>
  </el-dialog>
</template>

<style scoped>
.permission-tree-wrapper {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  padding: 8px;
  width: 100%;
}

.tree-node {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.tree-node-label {
  margin-left: 4px;
}
</style>
