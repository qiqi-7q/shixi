import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'


const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
// 测试记录路由（核心修复：确保component指向正确的组件）
  {
    path: '/test_record',
    name: 'TestRecord',
    component: () => import('../views/TestRecordView.vue'), // 这里必须和导入的变量名一致
    meta: { requiresAuth: false }
  },

  {
    path: '/',
    component: () => import('../components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/vehicles/resource'
      },
      {
        path: 'vehicles/resource',
        name: 'VehicleResource',
        component: () => import('../components/vehicle/VehicleResource.vue'),
        meta: { title: '车辆资源', requiresAuth: true }
      },
      {
        path: 'vehicles/borrow',
        name: 'VehicleBorrow',
        component: () => import('../components/vehicle/VehicleBorrow.vue'),
        meta: { title: '车辆借用记录', requiresAuth: true }
      }

    ]
  },
  // 默认重定向到登录页
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  console.log('路由守卫:', {
    to: to.path,
    requiresAuth: to.meta.requiresAuth,
    isAuthenticated: authStore.isAuthenticated
  })
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    console.log('未登录，跳转到登录页')
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    console.log('已登录，跳转到首页')
    next('/')
  } else {
    next()
  }
})

export default router