<template>
  <form @submit.prevent="handleSubmit" class="login-form">
    <div class="form-group">
      <label for="username">
        <i class="fas fa-user"></i>
        用户名
      </label>
      <input
        id="username"
        v-model="form.username"
        type="text"
        placeholder="请输入用户名"
        autocomplete="username"
        :class="{ error: errors.username }"
        @input="clearError('username')"
      />
      <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
    </div>

    <div class="form-group">
      <label for="password">
        <i class="fas fa-lock"></i>
        密码
      </label>
      <div class="password-input-wrapper">
        <input
          id="password"
          v-model="form.password"
          :type="showPassword ? 'text' : 'password'"
          placeholder="请输入密码"
          autocomplete="current-password"
          :class="{ error: errors.password }"
          @input="clearError('password')"
        />
        <button type="button" class="toggle-password" @click="showPassword = !showPassword">
          <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
        </button>
      </div>
      <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
    </div>

    <div class="form-options">
      <label class="checkbox-label">
        <input type="checkbox" v-model="form.remember" />
        <span>记住我</span>
      </label>
      <a href="#" class="forgot-password">忘记密码？</a>
    </div>

    <button type="submit" class="submit-btn" :disabled="loading">
      <i class="fas fa-sign-in-alt"></i>
      {{ loading ? '登录中...' : '登录' }}
    </button>

    <div v-if="formError" class="form-error">
      <i class="fas fa-exclamation-circle"></i>
      {{ formError }}
    </div>
  </form>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '../composables/useAuth'
import { useToast } from '../composables/useToast'

const emit = defineEmits(['login-success'])

const authStore = useAuthStore()
const toast = useToast()

const loading = ref(false)
const showPassword = ref(false)
const formError = ref('')

const form = reactive({
  username: '',
  password: '',
  remember: false
})

const errors = reactive({
  username: '',
  password: ''
})

const validate = () => {
  let isValid = true
  errors.username = ''
  errors.password = ''
  formError.value = ''

  if (!form.username.trim()) {
    errors.username = '请输入用户名'
    isValid = false
  }

  if (!form.password) {
    errors.password = '请输入密码'
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
    await authStore.login(form.username, form.password)
    toast.success('登录成功！')
    emit('login-success')
  } catch (error) {
    formError.value = error.message || '登录失败，请检查用户名和密码'
    toast.error(formError.value)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-form {
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

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.forgot-password {
  font-size: 0.875rem;
  color: var(--primary-color);
  text-decoration: none;
}

.forgot-password:hover {
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