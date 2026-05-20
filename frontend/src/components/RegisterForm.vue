<template>
  <form @submit.prevent="handleSubmit" class="register-form">
    <div class="form-group">
      <label for="reg-username">
        <i class="fas fa-user"></i>
        用户名
      </label>
      <input
        id="reg-username"
        v-model="form.username"
        type="text"
        placeholder="请输入用户名（3-20位字符）"
        :class="{ error: errors.username }"
        @input="clearError('username')"
      />
      <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
    </div>

    <div class="form-group">
      <label for="reg-email">
        <i class="fas fa-envelope"></i>
        邮箱
      </label>
      <input
        id="reg-email"
        v-model="form.email"
        type="email"
        placeholder="请输入邮箱地址"
        :class="{ error: errors.email }"
        @input="clearError('email')"
      />
      <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
    </div>

    <div class="form-group">
      <label for="reg-fullname">
        <i class="fas fa-id-card"></i>
        姓名
      </label>
      <input
        id="reg-fullname"
        v-model="form.full_name"
        type="text"
        placeholder="请输入真实姓名（选填）"
      />
    </div>

    <div class="form-group">
      <label for="reg-password">
        <i class="fas fa-lock"></i>
        密码
      </label>
      <div class="password-input-wrapper">
        <input
          id="reg-password"
          v-model="form.password"
          :type="showPassword ? 'text' : 'password'"
          placeholder="请输入密码（至少6位）"
          :class="{ error: errors.password }"
          @input="clearError('password')"
        />
        <button type="button" class="toggle-password" @click="showPassword = !showPassword">
          <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
        </button>
      </div>
      <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
    </div>

    <div class="form-group">
      <label for="reg-confirm-password">
        <i class="fas fa-check-circle"></i>
        确认密码
      </label>
      <div class="password-input-wrapper">
        <input
          id="reg-confirm-password"
          v-model="form.confirm_password"
          :type="showConfirmPassword ? 'text' : 'password'"
          placeholder="请再次输入密码"
          :class="{ error: errors.confirm_password }"
          @input="clearError('confirm_password')"
        />
        <button type="button" class="toggle-password" @click="showConfirmPassword = !showConfirmPassword">
          <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
        </button>
      </div>
      <span v-if="errors.confirm_password" class="error-message">{{ errors.confirm_password }}</span>
    </div>

    <div class="form-terms">
      <label class="checkbox-label">
        <input type="checkbox" v-model="form.agree_terms" />
        <span>我已阅读并同意 <a href="#">服务条款</a> 和 <a href="#">隐私政策</a></span>
      </label>
      <span v-if="errors.agree_terms" class="error-message">{{ errors.agree_terms }}</span>
    </div>

    <button type="submit" class="submit-btn" :disabled="loading">
      <i class="fas fa-user-plus"></i>
      {{ loading ? '注册中...' : '注册' }}
    </button>

    <div v-if="formError" class="form-error">
      <i class="fas fa-exclamation-circle"></i>
      {{ formError }}
    </div>
  </form>
</template>

<script setup>
import { ref, reactive } from 'vue'
//import { useAuthStore } from '../composables/useAuth'
import { useAuthStore } from '../stores/auth'  // 确保路径正确
import { useToast } from '../composables/useToast'

const emit = defineEmits(['register-success'])

const authStore = useAuthStore()
const toast = useToast()

const loading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const formError = ref('')

const form = reactive({
  username: '',
  email: '',
  full_name: '',
  password: '',
  confirm_password: '',
  agree_terms: false
})

const errors = reactive({
  username: '',
  email: '',
  password: '',
  confirm_password: '',
  agree_terms: ''
})

const validate = () => {
  let isValid = true
  Object.keys(errors).forEach(key => errors[key] = '')
  formError.value = ''

  // 用户名验证
  if (!form.username.trim()) {
    errors.username = '请输入用户名'
    isValid = false
  } else if (form.username.length < 3 || form.username.length > 20) {
    errors.username = '用户名长度应为3-20位字符'
    isValid = false
  } else if (!/^[a-zA-Z0-9_]+$/.test(form.username)) {
    errors.username = '用户名只能包含字母、数字和下划线'
    isValid = false
  }

  // 邮箱验证
  if (!form.email.trim()) {
    errors.email = '请输入邮箱地址'
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = '请输入有效的邮箱地址'
    isValid = false
  }

  // 密码验证
  if (!form.password) {
    errors.password = '请输入密码'
    isValid = false
  } else if (form.password.length < 6) {
    errors.password = '密码长度至少为6位'
    isValid = false
  }

  // 确认密码验证
  if (form.password !== form.confirm_password) {
    errors.confirm_password = '两次输入的密码不一致'
    isValid = false
  }

  // 协议同意验证
  if (!form.agree_terms) {
    errors.agree_terms = '请阅读并同意服务条款和隐私政策'
    isValid = false
  }

  return isValid
}

const clearError = (field) => {
  errors[field] = ''
  formError.value = ''
}

const handleSubmit = async () => {
  if (!validate()) return

  loading.value = true
  formError.value = ''

  try {
    const userData = {
      username: form.username,
      email: form.email,
      full_name: form.full_name || undefined,
      password: form.password
    }
    
    //await authStore.register(userData)
	// 调用 register 方法
    const result = await authStore.register(userData)
    console.log('Register result:', result)
    toast.success('注册成功！请登录')
    emit('register-success')
  } catch (error) {
    formError.value = error.message || '注册失败，请稍后重试'
    toast.error(formError.value)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-form {
  width: 100%;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.form-group label i {
  color: var(--primary-color);
  width: 1rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 1rem;
  transition: all 0.3s;
}

.password-input-wrapper {
  position: relative;
}

.password-input-wrapper input {
  padding-right: 2.5rem;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.form-group input.error {
  border-color: var(--danger-color);
}

.toggle-password {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  padding: 0.25rem;
}

.toggle-password:hover {
  color: var(--text-secondary);
}

.error-message {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: var(--danger-color);
}

.form-terms {
  margin-bottom: 1.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.checkbox-label input[type="checkbox"] {
  width: 1rem;
  height: 1rem;
  cursor: pointer;
}

.checkbox-label a {
  color: var(--primary-color);
  text-decoration: none;
}

.checkbox-label a:hover {
  text-decoration: underline;
}

.submit-btn {
  width: 100%;
  padding: 0.875rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.form-error {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: #FEE2E2;
  color: #991B1B;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>