import { defineStore } from 'pinia'
import { ref } from 'vue'
import { borrowAPI } from '../api/borrow'

export const useBorrowStore = defineStore('borrow', () => {
  const records = ref([])
  const loading = ref(false)
  const stats = ref({
    total: 0,
    active: 0,
    returned: 0,
    cancelled: 0
  })
  
  const fetchBorrowRecords = async (params = {}) => {
    loading.value = true
    try {
      records.value = await borrowAPI.getBorrowRecords(params)
      await fetchStats()
    } finally {
      loading.value = false
    }
  }
  
  const fetchStats = async () => {
    stats.value = await borrowAPI.getBorrowStats()
  }
  
  const createBorrowRecord = async (data) => {
    const record = await borrowAPI.createBorrowRecord(data)
    records.value.unshift(record)
    await fetchStats()
    return record
  }
  
  const returnVehicle = async (id) => {
    const record = await borrowAPI.returnVehicle(id)
    const index = records.value.findIndex(r => r.id === id)
    if (index > -1) {
      records.value[index] = record
    }
    await fetchStats()
    return record
  }
  
  const cancelBorrow = async (id) => {
    const record = await borrowAPI.cancelBorrow(id)
    const index = records.value.findIndex(r => r.id === id)
    if (index > -1) {
      records.value[index] = record
    }
    await fetchStats()
    return record
  }
  
  return {
    records,
    loading,
    stats,
    fetchBorrowRecords,
    fetchStats,
    createBorrowRecord,
    returnVehicle,
    cancelBorrow
  }
})