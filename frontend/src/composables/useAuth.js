import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { authAPI } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token') || null)
  
  const isAuthenticated = computed(() => !!token.value)
  const userName = computed(() => user.value?.full_name || user.value?.username || '用户')
  
  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('access_token', newToken)
  }
  
  const setUser = (userData) => {
    user.value = userData
  }
  
  const login = async (username, password) => {
    const data = await authAPI.login(username, password)
    setToken(data.access_token)
    
    // 获取用户信息
    try {
      const userData = await authAPI.getCurrentUser()
      setUser(userData)
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
    
    return data
  }
  
  const register = async (userData) => {
    return await authAPI.register(userData)
  }
  
  const logout = async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('access_token')
    }
  }
  
  const fetchUser = async () => {
    if (!token.value) return
    
    try {
      const userData = await authAPI.getCurrentUser()
      setUser(userData)
    } catch (error) {
      console.error('获取用户信息失败:', error)
      logout()
    }
  }
  
  return {
    user,
    token,
    isAuthenticated,
    userName,
    login,
    register,
    logout,
    fetchUser
  }
})