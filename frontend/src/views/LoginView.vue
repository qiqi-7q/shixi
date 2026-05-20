<template>
  <div class="login-container">
    <!-- 左侧装饰区域 -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="logo">
          <i class="fas fa-car-side"></i>
          <span>TestPlatform</span>
        </div>
        <h1>测试管理平台</h1>
        <p class="hero-description">
          高效管理车辆资源，简化测试流程
        </p>
        <div class="feature-list">
          <div class="feature-item">
            <i class="fas fa-car"></i>
            <span>车辆信息管理</span>
          </div>
          <div class="feature-item">
            <i class="fas fa-calendar-check"></i>
            <span>车辆借用预约</span>
          </div>
          <div class="feature-item">
            <i class="fas fa-chart-line"></i>
            <span>数据统计分析</span>
          </div>
          <div class="feature-item">
            <i class="fas fa-plug"></i>
            <span>插件化扩展</span>
          </div>
        </div>
        <div class="hero-footer">
          <p>© 2026 测试管理平台. All rights reserved.</p>
        </div>
      </div>
    </div>

    <!-- 右侧表单区域 -->
    <div class="form-section">
      <div class="form-container">
        <!-- 标签切换 -->
        <div class="form-tabs">
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'login' }"
            @click="activeTab = 'login'"
          >
            登录
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'register' }"
            @click="activeTab = 'register'"
          >
            注册
          </button>
        </div>

        <!-- 登录表单 -->
        <LoginForm 
          v-if="activeTab === 'login'"
          @login-success="handleLoginSuccess"
        />

        <!-- 注册表单 -->
        <RegisterForm 
          v-else
          @register-success="handleRegisterSuccess"
        />
      </div>
    </div>

    <!-- Toast 容器 -->
    <ToastContainer />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import LoginForm from '../components/LoginForm.vue'
import RegisterForm from '../components/RegisterForm.vue'
import ToastContainer from '../components/ToastContainer.vue'

const router = useRouter()
const activeTab = ref('login')

const handleLoginSuccess = () => {
  router.push('/vehicles/resource')
}

const handleRegisterSuccess = () => {
  activeTab.value = 'login'
}
</script>

<style scoped>
.login-container {
  display: flex;
  width: 100%;
  min-height: 100vh;
}

/* 左侧装饰区域 */
.hero-section {
  flex: 1;
  background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  padding: 3rem;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  animation: rotate 30s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 500px;
  margin: 0 auto;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 3rem;
}

.logo i {
  font-size: 2rem;
}

.hero-section h1 {
  font-size: 3rem;
  font-weight: 800;
  color: white;
  margin-bottom: 1rem;
  line-height: 1.2;
}

.hero-description {
  font-size: 1.125rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 3rem;
}

.feature-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 4rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: white;
}

.feature-item i {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-md);
  font-size: 1rem;
}

.hero-footer {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.875rem;
}

/* 右侧表单区域 */
.form-section {
  width: 480px;
  background: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  box-shadow: var(--shadow-xl);
}

.form-container {
  width: 100%;
  max-width: 400px;
}

.form-tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid var(--border-color);
}

.tab-btn {
  flex: 1;
  padding: 0.75rem;
  border: none;
  background: none;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  position: relative;
  transition: all 0.3s;
}

.tab-btn.active {
  color: var(--primary-color);
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--primary-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-section {
    display: none;
  }
  
  .form-section {
    width: 100%;
    padding: 1.5rem;
  }
  
  .form-container {
    max-width: 100%;
  }
}
</style>