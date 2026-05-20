<template>
  <div class="toast-container">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast', toast.type]"
        @click="removeToast(toast.id)"
      >
        <i :class="['fas', getIcon(toast.type)]"></i>
        <span class="message">{{ toast.message }}</span>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useToast } from '../composables/useToast'

const { toasts, removeToast } = useToast()

const getIcon = (type) => {
  const icons = {
    success: 'fa-check-circle',
    error: 'fa-exclamation-circle',
    warning: 'fa-exclamation-triangle',
    info: 'fa-info-circle'
  }
  return icons[type] || 'fa-info-circle'
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.toast {
  min-width: 300px;
  padding: 1rem 1.5rem;
  background: white;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  border-left: 4px solid;
}

.toast.success {
  border-left-color: var(--secondary-color);
}

.toast.error {
  border-left-color: var(--danger-color);
}

.toast.warning {
  border-left-color: var(--warning-color);
}

.toast.info {
  border-left-color: var(--primary-color);
}

.toast i {
  font-size: 1.25rem;
}

.toast.success i { color: var(--secondary-color); }
.toast.error i { color: var(--danger-color); }
.toast.warning i { color: var(--warning-color); }
.toast.info i { color: var(--primary-color); }

.toast .message {
  flex: 1;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>