<template>
  <div class="test_record-view">
    <!-- 页面标题 -->
    <h2 class="page-title">测试记录管理</h2>

    <!-- 操作栏 -->
    <div class="action-bar">
      <!-- 搜索框 -->
      <div class="search-box">
        <input
          v-model="keyword"
          type="text"
          placeholder="搜索项目/车型/VIN号/问题分类"
          @keyup.enter="handleSearch"
        >
        <button class="btn btn-primary" @click="handleSearch">搜索</button>
        <button class="btn btn-secondary" @click="resetSearch">重置</button>
      </div>

      <!-- 功能按钮 -->
      <div class="btn-group">
        <button class="btn btn-primary" @click="openAddDialog">新增记录</button>
        <label class="btn btn-success">
          导入Excel
          <input type="file" accept=".xlsx,.xls" @change="handleImport" hidden>
        </label>
        <button class="btn btn-info" @click="handleExport">导出Excel</button>
        <button class="btn btn-warning" @click="openFieldDialog">自定义字段</button>
      </div>
    </div>

    <!-- 列表区域 -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>项目</th>
            <th>车型</th>
            <th>VIN号</th>
            <th>问题分类</th>
            <th>问题时间</th>
            <th>分析人员</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in testRecordList" :key="item.id">
            <td>{{ item.project || '-' }}</td>
            <td>{{ item.car_model || '-' }}</td>
            <td>{{ item.car_vin || '-' }}</td>
            <td>{{ item.problem_category || '-' }}</td>
            <td>{{ formatDate(item.problem_time) }}</td>
            <td>{{ item.analysis_person || '-' }}</td>
            <td class="action-cell">
              <button class="btn btn-sm btn-primary" @click="openEditDialog(item)">编辑</button>
              <button class="btn btn-sm btn-danger" @click="handleDelete(item.id)">删除</button>
            </td>
          </tr>
          <tr v-if="testRecordList.length === 0 && !loading">
            <td colspan="7" class="empty-cell">暂无数据</td>
          </tr>
          <tr v-if="loading">
            <td colspan="7" class="loading-cell">
              <div class="loading-spinner"></div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div class="pagination" v-if="total > 0 && !loading">
        <span>共 {{ total }} 条记录</span>
        <div class="page-controls">
          <button
            class="btn btn-sm btn-secondary"
            @click="changePage(page - 1)"
            :disabled="page <= 1"
          >
            上一页
          </button>
          <span>第 {{ page }} 页 / 共 {{ totalPages }} 页</span>
          <button
            class="btn btn-sm btn-secondary"
            @click="changePage(page + 1)"
            :disabled="page >= totalPages"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <div class="dialog-overlay" v-if="dialogVisible" @click.self="closeDialog">
      <div class="dialog-content">
        <TestRecordFormDialog
          :visible="dialogVisible"
          :edit-data="editData"
          @close="closeDialog"
          @save="fetchData"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTestRecordStore } from '../stores/testRecord'
import TestRecordFormDialog from '../components/layout/TestRecordFormDialog.vue'
import { useToast } from '../composables/useToast'

const toast = useToast()
const testRecordStore = useTestRecordStore()

// 响应式数据
const keyword = ref('')
const dialogVisible = ref(false)
const fieldDialogVisible = ref(false)
const editData = ref({})
const newField = ref({
  field_name: '',
  field_code: '',
  field_type: 'text'
})

// 计算属性
const testRecordList = computed(() => testRecordStore.list)
const total = computed(() => testRecordStore.total)
const page = computed(() => testRecordStore.page)
const size = computed(() => testRecordStore.size)
const loading = computed(() => testRecordStore.loading)
const totalPages = computed(() => Math.ceil(total.value / size.value))

 //初始化
onMounted(() => {
  fetchData()
  testRecordStore.fetchTestRecordList()
})

// 获取数据列表
const fetchData = () => {
  testRecordStore.fetchTestRecordList()
}

// 搜索
const handleSearch = () => {
  testRecordStore.keyword = keyword.value
  testRecordStore.page = 1
  fetchData()
}

// 重置搜索
const resetSearch = () => {
  keyword.value = ''
  testRecordStore.resetSearch()
  fetchData()
}

// 切换页码
const changePage = (newPage) => {
  if (newPage < 1 || newPage > totalPages.value) return
  testRecordStore.page = newPage
  fetchData()
}

// 打开新增弹窗
const openAddDialog = () => {
  editData.value = {}
  dialogVisible.value = true
}

// 打开编辑弹窗
const openEditDialog = (item) => {
  editData.value = { ...item }
  dialogVisible.value = true
}

// 关闭弹窗
const closeDialog = () => {
  dialogVisible.value = false
}

// 打开自定义字段弹窗
const openFieldDialog = () => {
  newField.value = {
    field_name: '',
    field_code: '',
    field_type: 'text'
  }
  fieldDialogVisible.value = true
}

// 关闭自定义字段弹窗
const closeFieldDialog = () => {
  fieldDialogVisible.value = false
}


// 删除记录
const handleDelete = async (id) => {
  if (confirm('确定要删除这条记录吗？')) {
    await testRecordStore.deleteTestRecordData(id)
  }
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}
</script>

<style scoped>
.test_record-view {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #333;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.search-box {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-box input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 300px;
}

.btn-group {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.btn-success {
  background: #52c41a;
  color: white;
}

.btn-info {
  background: #40a9ff;
  color: white;
}

.btn-warning {
  background: #faad14;
  color: white;
}

.btn-danger {
  background: #ff4d4f;
  color: white;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.data-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.action-cell {
  display: flex;
  gap: 8px;
}

.empty-cell, .loading-cell {
  text-align: center;
  padding: 40px;
  color: #999;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #eee;
  border-top: 3px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-top: 1px solid #eee;
}

.page-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* 弹窗样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
}

.field-dialog {
  max-width: 500px;
}

.required {
  color: #ff4d4f;
}

.form-item {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-item input,
.form-item select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
</style>