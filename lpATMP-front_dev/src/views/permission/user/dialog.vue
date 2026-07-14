<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from "vue";
import "plus-pro-components/es/components/dialog-form/style/css";
import {
  type PlusColumn,
  type FieldValues,
  PlusDialogForm
} from "plus-pro-components";
import { getAuthRoleList } from "@/api/system";

const emit = defineEmits<{
  (e: "save", data: FieldValues): void;
}>();

const visible = ref(false);
const dialogKey = ref(0);
const values = ref<FieldValues>({});
const currentMode = ref<"add" | "edit" | "detail">("add");
const isDetail = computed(() => currentMode.value === "detail");
const isAdd = computed(() => currentMode.value === "add");
const roleOptions = ref<{ label: string; value: string }[]>([]);

const fetchRoles = async () => {
  try {
    const res: any = await getAuthRoleList();
    const result = res.data;
    let list: any[] = [];
    if (result && Array.isArray(result.items)) {
      list = result.items;
    } else if (Array.isArray(res)) {
      list = res;
    } else if (Array.isArray(result)) {
      list = result;
    }
    const seen = new Set<string>();
    roleOptions.value = list
      .filter((r: any) => {
        if (!r.code || seen.has(r.code)) return false;
        seen.add(r.code);
        return true;
      })
      .map((r: any) => ({ label: r.name, value: r.code }));
  } catch {
    roleOptions.value = [];
  }
};

const formColumns = computed<PlusColumn[]>(() => [
  {
    label: "账号",
    prop: "username",
    fieldProps: {
      placeholder: "请输入账号",
      disabled: isDetail.value || !isAdd.value,
      autocomplete: "off"
    },
    formItemProps: {
      rules: [
        { required: true, message: "请输入工号", trigger: "blur" },
        {
          pattern: /^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]+$/,
          message: "密码只能包含字母、数字和特殊字符，不能包含中文",
          trigger: "change"
        }
      ]
    }
  },
  {
    label: "密码",
    prop: "password",
    fieldProps: {
      type: "password",
      placeholder: isAdd.value ? "请输入密码" : "不修改请留空",
      disabled: isDetail.value,
      autocomplete: "new-password"
    },
    formItemProps: {
      rules: isAdd.value
        ? [
            { required: true, message: "请输入密码", trigger: "blur" },
            { min: 6, message: "密码长度至少6位", trigger: "blur" },
            {
              pattern: /^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]+$/,
              message: "密码只能包含字母、数字和特殊字符，不能包含中文",
              trigger: "blur"
            }
          ]
        : []
    }
  },
  {
    label: "姓名",
    prop: "full_name",
    fieldProps: {
      placeholder: "请输入姓名",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [{ required: true, message: "请输入姓名", trigger: "blur" }]
    }
  },
  {
    label: "邮箱",
    prop: "email",
    fieldProps: {
      placeholder: "请输入邮箱",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [
        { required: true, message: "请输入邮箱", trigger: "blur" },
        { type: "email", message: "请输入正确的邮箱格式", trigger: "blur" }
      ]
    }
  },
  {
    label: "角色",
    prop: "role",
    valueType: "select",
    options: roleOptions.value,
    fieldProps: {
      placeholder: "请选择角色",
      disabled: isDetail.value
    },
    formItemProps: {
      rules: [{ required: true, message: "请选择角色", trigger: "change" }]
    }
  },
  {
    label: "状态",
    prop: "is_active",
    valueType: "switch",
    fieldProps: {
      activeText: "启用",
      inactiveText: "禁用",
      disabled: isDetail.value
    }
  }
]);

const titleMap = {
  add: "新增用户",
  edit: "编辑用户",
  detail: "用户详情"
};

const dialogTitle = computed(() => titleMap[currentMode.value]);

const open = (mode: "add" | "edit" | "detail", data?: Record<string, any>) => {
  currentMode.value = mode;
  if (mode === "edit" || mode === "detail") {
    values.value = { ...(data || {}) };
  } else {
    values.value = {
      is_active: true
    };
  }
  nextTick(() => {
    dialogKey.value++;
    visible.value = true;
  });
};

onMounted(() => {
  fetchRoles();
});

const handleSubmit = (vals: FieldValues) => {
  // 编辑时密码为空则不传递
  if (!isAdd.value && !vals.password) {
    delete vals.password;
  }
  emit("save", vals);
  visible.value = false;
};

defineExpose({ open });
</script>

<template>
  <div class="permission-user-dialog">
    <PlusDialogForm
      :key="dialogKey"
      v-model:visible="visible"
      v-model="values"
      :form="{
        columns: formColumns,
        labelPosition: 'right',
        labelWidth: '120px'
      }"
      :title="dialogTitle"
      :show-submit-btn="currentMode !== 'detail'"
      :show-cancel-btn="true"
      confirm-text="保存"
      cancel-text="取消"
      @confirm="handleSubmit"
      :has-footer="currentMode !== 'detail'"
    />
  </div>
</template>
