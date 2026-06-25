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
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/views/HomeView.vue'),
          meta: { requiresAuth: true },
        },
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
        {
          path: 'sys/message',
          name: 'sys-message',
          component: () => import('@/views/sys/MessageView.vue'),
          meta: { requiresAuth: true, title: '消息管理' },
        },
        {
          path: 'sys/todo',
          name: 'sys-todo',
          component: () => import('@/views/sys/TodoView.vue'),
          meta: { requiresAuth: true, title: '待办管理' },
        },
        {
          path: 'sys/schedule',
          name: 'sys-schedule',
          component: () => import('@/views/sys/ScheduleView.vue'),
          meta: { requiresAuth: true, title: '日程管理' },
        },
        {
          path: 'sys/quick-entry',
          name: 'sys-quick-entry',
          component: () => import('@/views/sys/QuickEntryView.vue'),
          meta: { requiresAuth: true, title: '快捷入口' },
        },
        {
          path: 'sys/announcement',
          name: 'sys-announcement',
          component: () => import('@/views/sys/AnnouncementView.vue'),
          meta: { requiresAuth: true, title: '公告管理' },
        },
        {
          path: 'sys/announcement/:id',
          name: 'sys-announcement-detail',
          component: () => import('@/views/sys/AnnouncementDetailView.vue'),
          meta: { requiresAuth: true, title: '公告详情' },
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
