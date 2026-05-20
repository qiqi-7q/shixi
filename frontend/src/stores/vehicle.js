import { defineStore } from 'pinia'
import { ref } from 'vue'
import { vehicleAPI } from '../api/vehicle'

export const useVehicleStore = defineStore('vehicle', () => {
  const vehicles = ref([])
  const loading = ref(false)
  const stats = ref({
    total: 0,
    available: 0,
    borrowed: 0,
    maintenance: 0
  })
  
  const fetchVehicles = async (params = {}) => {
    loading.value = true
    try {
      vehicles.value = await vehicleAPI.getVehicles(params)
      await fetchStats()
    } finally {
      loading.value = false
    }
  }
  
  const fetchStats = async () => {
    stats.value = await vehicleAPI.getVehicleStats()
  }
  
  const createVehicle = async (data) => {
    const vehicle = await vehicleAPI.createVehicle(data)
    vehicles.value.push(vehicle)
    await fetchStats()
    return vehicle
  }
  
  const updateVehicle = async (id, data) => {
    const vehicle = await vehicleAPI.updateVehicle(id, data)
    const index = vehicles.value.findIndex(v => v.id === id)
    if (index > -1) {
      vehicles.value[index] = vehicle
    }
    await fetchStats()
    return vehicle
  }
  
  const deleteVehicle = async (id) => {
    await vehicleAPI.deleteVehicle(id)
    vehicles.value = vehicles.value.filter(v => v.id !== id)
    await fetchStats()
  }
  
  return {
    vehicles,
    loading,
    stats,
    fetchVehicles,
    fetchStats,
    createVehicle,
    updateVehicle,
    deleteVehicle
  }
})