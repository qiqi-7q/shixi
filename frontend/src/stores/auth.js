import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const token = ref(localStorage.getItem('access_token') || null)
  
  const isAuthenticated = computed(() => {
    console.log('isAuthenticated check:', !!token.value)
    return !!token.value
  })
  
  const userName = computed(() => user.value?.full_name || user.value?.username || '用户')
  
  const setToken = (newToken) => {
    console.log('setToken:', newToken)
    token.value = newToken
    localStorage.setItem('access_token', newToken)
  }
  
  const setUser = (userData) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }
  
  const login = async (username, password) => {
    console.log('login attempt:', username)
    const data = await authAPI.login(username, password)
    setToken(data.access_token)
    
    try {
      const userData = await authAPI.getCurrentUser()
      setUser(userData)
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
    
    return data
  }
  
   // 确保 register 方法存在
  const register = async (userData) => {
    console.log('Registering user:', userData)
    const data = await authAPI.register(userData)
    return data
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
      localStorage.removeItem('user')
    }
  }
  
  return {
    user,
    token,
    isAuthenticated,
    userName,
    login,
	register,  // 确保导出
    logout,
    setUser
  }
})