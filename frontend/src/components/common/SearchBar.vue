<template>
  <div class="search-bar">
    <form @submit.prevent="handleSearch">
      <div class="search-fields">
        <div 
          v-for="field in fields" 
          :key="field.name"
          class="search-field"
        >
          <label :for="field.name">{{ field.label }}</label>
          
          <input 
            v-if="field.type === 'text'"
            :id="field.name"
            v-model="formData[field.name]"
            type="text"
            :placeholder="`请输入${field.label}`"
          />
          
          <select 
            v-else-if="field.type === 'select'"
            :id="field.name"
            v-model="formData[field.name]"
          >
            <option 
              v-for="option in field.options" 
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
        </div>
      </div>
      
      <div class="search-actions">
        <button type="submit" class="btn-search">
          <i class="fas fa-search"></i>
          搜索
        </button>
        <button type="button" class="btn-reset" @click="handleReset">
          <i class="fas fa-redo-alt"></i>
          重置
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  fields: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['search', 'reset'])

const formData = reactive({})

// 初始化表单数据
props.fields.forEach(field => {
  formData[field.name] = ''
})

const handleSearch = () => {
  const params = {}
  Object.keys(formData).forEach(key => {
    if (formData[key]) {
      params[key] = formData[key]
    }
  })
  emit('search', params)
}

const handleReset = () => {
  props.fields.forEach(field => {
    formData[field.name] = ''
  })
  emit('reset')
}
</script>

<style scoped>
.search-bar {
  width: 100%;
}

.search-fields {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.search-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.search-field label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.search-field input,
.search-field select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  transition: all 0.3s;
}

.search-field input:focus,
.search-field select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}

.search-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-search,
.btn-reset {
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s;
}

.btn-search {
  background: var(--primary-color);
  color: white;
}

.btn-search:hover {
  background: var(--primary-dark);
}

.btn-reset {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.btn-reset:hover {
  background: var(--border-color);
}
</style>