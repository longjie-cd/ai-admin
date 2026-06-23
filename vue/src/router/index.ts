import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true },
      redirect: '/sys/user',
      children: [
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/ProfileView.vue'),
          meta: { requiresAuth: true, title: '个人中心' },
        },
        {
          path: 'sys/user',
          name: 'sys-user',
          component: () => import('@/views/sys/UserView.vue'),
          meta: { requiresAuth: true, title: '用户管理' },
        },
        {
          path: 'sys/team',
          name: 'sys-team',
          component: () => import('@/views/sys/TeamView.vue'),
          meta: { requiresAuth: true, title: '团队管理' },
        },
        {
          path: 'sys/role',
          name: 'sys-role',
          component: () => import('@/views/sys/RoleView.vue'),
          meta: { requiresAuth: true, title: '角色管理' },
        },
        {
          path: 'sys/permission',
          name: 'sys-permission',
          component: () => import('@/views/sys/PermissionView.vue'),
          meta: { requiresAuth: true, title: '权限管理' },
        },
        {
          path: 'sys/dict',
          name: 'sys-dict',
          component: () => import('@/views/sys/DictView.vue'),
          meta: { requiresAuth: true, title: '数据字典' },
        },
        {
          path: 'sys/api',
          name: 'sys-api',
          component: () => import('@/views/sys/ApiView.vue'),
          meta: { requiresAuth: true, title: 'API 管理' },
        },
        {
          path: 'sys/menu',
          name: 'sys-menu',
          component: () => import('@/views/sys/MenuView.vue'),
          meta: { requiresAuth: true, title: '菜单管理' },
        },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.token) {
    return { name: 'login' }
  }
})

export default router
