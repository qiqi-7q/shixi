<template>
  <aside class="app-sidebar">
    <div class="sidebar-header">
      <i class="fas fa-car-side"></i>
      <span>测试管理平台</span>
    </div>
    
    <nav class="sidebar-nav">
      <div class="nav-section">
        <div 
          class="nav-item has-submenu"
          :class="{ expanded: expandedMenus.includes('vehicle') }"
        >
          <div class="nav-item-header" @click="toggleMenu('vehicle')">
            <div class="nav-item-title">
              <i class="fas fa-car"></i>
              <span>车辆管理</span>
            </div>
            <i class="fas fa-chevron-down arrow"></i>
          </div>
          
          <div v-show="expandedMenus.includes('vehicle')" class="submenu">
            <router-link 
              to="/vehicles/resource" 
              class="submenu-item"
              :class="{ active: route.path === '/vehicles/resource' }"
            >
              <i class="fas fa-list"></i>
              <span>车辆资源</span>
            </router-link>
            
            <router-link 
              to="/vehicles/borrow" 
              class="submenu-item"
              :class="{ active: route.path === '/vehicles/borrow' }"
            >
              <i class="fas fa-calendar-alt"></i>
              <span>车辆借用记录</span>
            </router-link>

            <router-link to="/test-record" class="nav-item">测试记录</router-link>
          </div>
        </div>
      </div>
    </nav>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const expandedMenus = ref(['vehicle'])

const toggleMenu = (menu) => {
  const index = expandedMenus.value.indexOf(menu)
  if (index > -1) {
    expandedMenus.value.splice(index, 1)
  } else {
    expandedMenus.value.push(menu)
  }
}
</script>

<style scoped>
.app-sidebar {
  width: 260px;
  background: white;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-sm);
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0 1.5rem;
  border-bottom: 1px solid var(--border-color);
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--primary-color);
}

.sidebar-header i {
  font-size: 1.5rem;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
}

.nav-section {
  padding: 0 0.75rem;
}

.nav-item {
  margin-bottom: 0.25rem;
}

.nav-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.3s;
}

.nav-item-header:hover {
  background: var(--bg-secondary);
}

.nav-item-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--text-primary);
  font-weight: 500;
}

.nav-item-title i {
  width: 1.25rem;
  color: var(--primary-color);
}

.arrow {
  font-size: 0.75rem;
  color: var(--text-light);
  transition: transform 0.3s;
}

.nav-item.expanded .arrow {
  transform: rotate(180deg);
}

.submenu {
  padding-left: 2.5rem;
  margin-top: 0.25rem;
}

.submenu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 1rem;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.3s;
  font-size: 0.875rem;
}

.submenu-item:hover {
  background: var(--bg-secondary);
  color: var(--primary-color);
}

.submenu-item.active {
  background: var(--primary-color);
  color: white;
}

.submenu-item i {
  width: 1rem;
  font-size: 0.875rem;
}
</style>