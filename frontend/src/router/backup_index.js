import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
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
        meta: { title: '车辆资源' }
      },
      {
        path: 'vehicles/borrow',
        name: 'VehicleBorrow',
        component: () => import('../components/vehicle/VehicleBorrow.vue'),
        meta: { title: '车辆借用记录' }
      }
    ]
  },
  // 添加默认重定向
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
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router