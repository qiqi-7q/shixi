<script setup lang="ts">
import Motion from "./utils/motion";
import { useRouter } from "vue-router";
import { message } from "@/utils/message";
import { loginRules } from "./utils/rule";
import { ref, reactive, toRaw, onMounted } from "vue";
import { debounce } from "@pureadmin/utils";
import { useNav } from "@/layout/hooks/useNav";
import { useEventListener } from "@vueuse/core";
import type { FormInstance } from "element-plus";
import { useLayout } from "@/layout/hooks/useLayout";
import { useUserStoreHook } from "@/store/modules/user";
import { initRouter, getTopMenu } from "@/router/utils";
import { bg, avatar, illustration } from "./utils/static";
import { useRenderIcon } from "@/components/ReIcon/src/hooks";
import { useDataThemeChange } from "@/layout/hooks/useDataThemeChange";
import { register, forgetPassword } from "@/api/system";
import { getMe } from "@/api/user";
import { setToken, formatToken } from "@/utils/auth";

import dayIcon from "@/assets/svg/day.svg?component";
import darkIcon from "@/assets/svg/dark.svg?component";
import Lock from "~icons/ri/lock-fill";
import User from "~icons/ri/user-3-fill";

defineOptions({
  name: "Login"
});

const router = useRouter();
const loading = ref(false);
const disabled = ref(false);
const ruleFormRef = ref<FormInstance>();

// 背景视频循环播放
const videoList = ["/video.mp4"];
const currentVideoIndex = ref(0);
const videoSrc = ref(videoList[0]);
const videoRef = ref<HTMLVideoElement>();
const videoLoading = ref(true);

function onVideoEnded() {
  currentVideoIndex.value = (currentVideoIndex.value + 1) % videoList.length;
  videoSrc.value = videoList[currentVideoIndex.value];
}

function onVideoLoaded() {
  videoLoading.value = false;
}

onMounted(() => {
  if (videoRef.value) {
    videoRef.value.addEventListener("ended", onVideoEnded);
  }
});

const { initStorage } = useLayout();
initStorage();

const { dataTheme, overallStyle, dataThemeChange } = useDataThemeChange();
dataThemeChange(overallStyle.value);
const { title } = useNav();

const ruleForm = reactive({
  username: "",
  password: ""
});

const onLogin = async (formEl: FormInstance | undefined) => {
  if (!formEl) return;
  await formEl.validate(valid => {
    if (valid) {
      loading.value = true;
      useUserStoreHook()
        .loginByUsername({
          username: ruleForm.username,
          password: ruleForm.password
        })
        .then(res => {
          console.log("res:", res);
          if (res.success) {
            return initRouter().then(() => {
              disabled.value = true;
              router
                .push(getTopMenu(true).path)
                .then(() => {
                  message("登录成功", { type: "success" });
                })
                .finally(() => (disabled.value = false));
            });
          } else {
            message(res.message || "登录失败", { type: "error" });
          }
        })
        .finally(() => (loading.value = false));
    }
  });
};

const immediateDebounce: any = debounce(
  formRef => onLogin(formRef),
  1000,
  true
);

useEventListener(document, "keydown", ({ code }) => {
  if (
    ["Enter", "NumpadEnter"].includes(code) &&
    !disabled.value &&
    !loading.value
  )
    immediateDebounce(ruleFormRef.value);
});

// ==================== 注册 ====================
const registerDialogVisible = ref(false);
const registerLoading = ref(false);
const registerFormRef = ref<FormInstance>();
const registerForm = reactive({
  username: "",
  email: "",
  full_name: "",
  password: ""
});

const registerRules = {
  username: [
    { required: true, message: "请输入工号", trigger: "blur" },
    {
      pattern: /^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]+$/,
      message: "密码只能包含字母、数字和特殊字符，不能包含中文",
      trigger: "change"
    }
  ],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "请输入正确的邮箱格式", trigger: "blur" }
  ],
  full_name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码长度至少6位", trigger: "blur" },
    {
      pattern: /^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]+$/,
      message: "密码只能包含字母、数字和特殊字符，不能包含中文",
      trigger: "blur"
    }
  ]
};

function openRegister() {
  registerForm.username = "";
  registerForm.email = "";
  registerForm.full_name = "";
  registerForm.password = "";
  registerDialogVisible.value = true;
}

async function handleRegister(formEl: FormInstance | undefined) {
  if (!formEl) return;
  await formEl.validate(async valid => {
    if (!valid) return;
    registerLoading.value = true;
    try {
      const body: any = {
        username: registerForm.username,
        email: registerForm.email,
        full_name: registerForm.full_name,
        password: registerForm.password
      };
      const res: any = await register(body);
      if (res.code === 201 || res.code === 200) {
        const token = res?.data?.access_token;
        if (token) {
          // 调用 /api/auth/me 获取完整用户信息
          try {
            const meRes: any = await getMe({
              headers: { Authorization: formatToken(token) }
            });
            const meData = meRes?.data || {};
            setToken({
              ...res.data,
              ...(res.data.user || {}),
              accessToken: token,
              refreshToken: token,
              expires: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
              full_name: meData.full_name || "",
              avatar: meData.avatar || "",
              nickname: meData.nickname || meData.full_name || "",
              roles: meData.role ? [meData.role] : [],
              permissions: meData.permissions || []
            } as any);
          } catch {
            // 获取用户信息失败，使用注册返回的兜底数据
            setToken({
              ...res.data,
              ...res.data.user,
              accessToken: token,
              refreshToken: token,
              expires: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
              full_name: res.data.user?.full_name ?? "",
              roles: res.data.user?.role ? [res.data.user.role] : [],
              permissions: ["superuser", "admin"].includes(res.data.user?.role)
                ? ["*"]
                : []
            } as any);
          }
          message("注册成功，正在登录...", { type: "success" });
          registerDialogVisible.value = false;
          await initRouter();
          router.push("/welcome");
        } else {
          message("注册成功，请登录", { type: "success" });
          registerDialogVisible.value = false;
          ruleForm.username = registerForm.username;
        }
      } else {
        message(res.message || res.detail || "注册失败", { type: "error" });
      }
    } catch (e: any) {
      const errMsg =
        e?.response?.data?.detail ||
        e?.response?.data?.message ||
        e?.message ||
        "注册失败";
      message(errMsg, { type: "error" });
    } finally {
      registerLoading.value = false;
    }
  });
}

// ==================== 忘记密码 ====================
const forgetDialogVisible = ref(false);
const forgetLoading = ref(false);
const forgetFormRef = ref<FormInstance>();
const forgetForm = reactive({
  username: ""
});
const forgetResult = ref<{
  username: string;
  email: string;
} | null>(null);

function openForget() {
  forgetForm.username = "";
  forgetResult.value = null;
  forgetDialogVisible.value = true;
}

async function handleForget(formEl: FormInstance | undefined) {
  if (!formEl) return;
  await formEl.validate(async valid => {
    if (!valid) return;
    forgetLoading.value = true;
    forgetResult.value = null;
    try {
      const res: any = await forgetPassword({ username: forgetForm.username });
      if (res.code === 200 && res.data) {
        forgetResult.value = {
          username: res.data.username,
          email: res.data.email
        };
        message("密码已发送到您的邮箱，请查收", { type: "success" });
      } else {
        message(res.message || res.detail || "用户不存在", { type: "error" });
      }
    } catch (e: any) {
      const errMsg =
        e?.response?.data?.detail ||
        e?.response?.data?.message ||
        e?.message ||
        "用户不存在";
      message(errMsg, { type: "error" });
    } finally {
      forgetLoading.value = false;
    }
  });
}

/** 使用忘记密码查到的账号直接登录 */
async function loginWithForgetAccount(data: {
  username: string;
  password: string;
}) {
  ruleForm.username = data.username;
  ruleForm.password = data.password;
  forgetDialogVisible.value = false;
  loading.value = true;
  try {
    const res = await useUserStoreHook().loginByUsername({
      username: data.username,
      password: data.password
    });
    if (res.success) {
      await initRouter();
      disabled.value = true;
      await router.push(getTopMenu(true).path);
      message("登录成功", { type: "success" });
    } else {
      message(res.message || "登录失败", { type: "error" });
    }
  } catch (e: any) {
    message(e?.message || "登录失败", { type: "error" });
  } finally {
    loading.value = false;
    disabled.value = false;
  }
}
</script>

<template>
  <div class="select-none">
    <!-- 背景视频 -->
    <video
      ref="videoRef"
      class="bg-video"
      autoplay
      muted
      playsinline
      loop
      preload="auto"
      :src="videoSrc"
      @loadeddata="onVideoLoaded"
    />
    <div class="login-container">
      <div class="img">
        <!-- <component :is="toRaw(illustration)" /> -->
      </div>
      <div class="login-box">
        <div class="login-form">
          <img :src="avatar" class="avatar" />

          <el-form
            ref="ruleFormRef"
            :model="ruleForm"
            :rules="loginRules"
            size="large"
          >
            <Motion :delay="100">
              <el-form-item
                :rules="[
                  {
                    required: true,
                    message: '请输入工号',
                    trigger: 'blur'
                  }
                ]"
                prop="username"
              >
                <el-input
                  v-model="ruleForm.username"
                  clearable
                  placeholder="账号"
                  :prefix-icon="useRenderIcon(User)"
                />
              </el-form-item>
            </Motion>

            <Motion :delay="150">
              <el-form-item prop="password">
                <el-input
                  v-model="ruleForm.password"
                  clearable
                  show-password
                  placeholder="密码"
                  :prefix-icon="useRenderIcon(Lock)"
                />
              </el-form-item>
            </Motion>

            <Motion :delay="250">
              <el-button
                class="w-full mt-4!"
                size="default"
                type="primary"
                :loading="loading"
                :disabled="disabled"
                @click="onLogin(ruleFormRef)"
              >
                登录
              </el-button>
            </Motion>

            <Motion :delay="300">
              <div class="flex justify-between mt-3 text-sm">
                <el-button link type="primary" @click="openRegister">
                  用户注册
                </el-button>
                <el-button link type="primary" @click="openForget">
                  忘记密码
                </el-button>
              </div>
            </Motion>
          </el-form>
        </div>
      </div>
    </div>

    <!-- 注册弹窗 -->
    <el-dialog
      v-model="registerDialogVisible"
      title="用户注册"
      width="420px"
      top="25vh"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="80px"
        size="large"
      >
        <el-form-item label="账号" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入工号"
            autocomplete="username"
          />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱"
            autocomplete="email"
          />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input
            v-model="registerForm.full_name"
            placeholder="请输入姓名"
            autocomplete="name"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            show-password
            placeholder="请输入密码"
            autocomplete="new-password"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="registerDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="registerLoading"
          @click="handleRegister(registerFormRef)"
        >
          注册
        </el-button>
      </template>
    </el-dialog>

    <!-- 忘记密码弹窗 -->
    <el-dialog
      v-model="forgetDialogVisible"
      title="忘记密码"
      width="420px"
      top="25vh"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <!-- 查询表单 -->
      <div v-if="!forgetResult" class="px-2">
        <el-form
          ref="forgetFormRef"
          :model="forgetForm"
          label-width="80px"
          size="large"
        >
          <el-form-item
            label="账号"
            prop="username"
            :rules="[
              { required: true, message: '请输入工号', trigger: 'blur' }
            ]"
          >
            <el-input v-model="forgetForm.username" placeholder="请输入工号" />
          </el-form-item>
        </el-form>
      </div>
      <!-- 查询结果 -->
      <div v-else class="px-2">
        <el-descriptions :column="1" border size="large">
          <el-descriptions-item label="账号" label-class-name="font-medium">
            {{ forgetResult.username }}
          </el-descriptions-item>
          <el-descriptions-item label="邮箱" label-class-name="font-medium">
            {{ forgetResult.email }}
          </el-descriptions-item>
        </el-descriptions>
        <el-alert
          class="mt-4"
          title="密码已发送到您的邮箱，请使用邮箱中的密码登录"
          type="success"
          :closable="false"
          show-icon
        />
      </div>

      <template #footer>
        <span v-if="!forgetResult">
          <el-button @click="forgetDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="forgetLoading"
            @click="handleForget(forgetFormRef)"
          >
            查询
          </el-button>
        </span>
        <span v-else>
          <el-button type="primary" @click="forgetDialogVisible = false">
            关闭
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
@import url("@/style/login.css");
</style>

<style lang="scss" scoped>
.bg-video {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  object-fit: cover;
  z-index: -1;
  background: linear-gradient(135deg, #667eea 0%, #616370 100%);
  transition: opacity 0.3s ease;
}

:deep(.el-input-group__append, .el-input-group__prepend) {
  padding: 0;
}
.avatar {
  overflow: hidden;
  object-fit: cover;
  img {
    width: 100%;
    height: 100%;
  }
}

/* 弹窗统一样式 */
:deep(.el-dialog) {
  border-radius: 12px;
  --el-dialog-bg-color: #fff;

  .el-dialog__header {
    padding: 20px 20px 0px;
    margin-bottom: 8px;

    .el-dialog__title {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }
  }

  .el-dialog__body {
    padding: 8px 0% 0px;
    margin-bottom: 20px;
  }

  .el-dialog__footer {
    padding: 0 0% 0px;
    border-top: none;
  }

  .el-form-item {
    margin-bottom: 22px;

    .el-form-item__label {
      font-weight: 500;
      color: #606266;
    }
  }

  .el-descriptions {
    .el-descriptions__cell {
      padding: 12px 16px;

      .el-tag {
        font-size: 14px;
        padding: 0 12px;
        height: 32px;
        line-height: 32px;
      }
    }
  }

  .el-alert {
    border-radius: 8px;
    padding: 10px 14px;
  }
}

/* 暗色模式适配 */
:root.dark {
  :deep(.el-dialog) {
    --el-dialog-bg-color: #1d1e1f;

    .el-dialog__title {
      color: var(--el-text-color-primary);
    }
  }
}
:deep(input:-webkit-autofill) {
  -webkit-box-shadow: 0 0 0 1000px transparent inset !important;
  box-shadow: 0 0 0 1000px transparent inset !important;
  -webkit-text-fill-color: inherit !important;
  transition: background-color 5000s ease-in-out 0s;
}
</style>
