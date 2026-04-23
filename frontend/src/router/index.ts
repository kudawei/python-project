/**
 * Vue Router 路由配置
 * 定义项目的页面路由结构和导航守卫。
 */

import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
      meta: { title: '登录', requiresAuth: false },
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { title: '注册', requiresAuth: false },
    },
    {
      path: '/',
      component: () => import('@/views/LayoutView.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          redirect: '/dashboard',
        },
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/DashboardView.vue'),
          meta: { title: '数据看板' },
        },
        {
          path: 'profile',
          name: 'Profile',
          component: () => import('@/views/ProfileView.vue'),
          meta: { title: '考研意向画像' },
        },
        {
          path: 'search',
          name: 'Search',
          component: () => import('@/views/SearchView.vue'),
          meta: { title: '多维检索' },
        },
        {
          path: 'recommend',
          name: 'Recommend',
          component: () => import('@/views/RecommendView.vue'),
          meta: { title: '智能推荐' },
        },
        {
          path: 'favorites',
          name: 'Favorites',
          component: () => import('@/views/FavoritesView.vue'),
          meta: { title: '我的收藏' },
        },
        {
          path: 'compare',
          name: 'Compare',
          component: () => import('@/views/CompareView.vue'),
          meta: { title: '院校对比' },
        },
        {
          path: 'recommend-history',
          name: 'RecommendHistory',
          component: () => import('@/views/RecommendHistoryView.vue'),
          meta: { title: '推荐历史' },
        },
        {
          path: 'data/major',
          name: 'DataMajor',
          component: () => import('@/views/DataMajorView.vue'),
          meta: { title: '专业信息表' },
        },
        {
          path: 'data/major-university',
          name: 'DataMajorUniversity',
          component: () => import('@/views/DataMajorUniversityView.vue'),
          meta: { title: '专业-院校关联表' },
        },
        {
          path: 'data/major-detail',
          name: 'DataMajorDetail',
          component: () => import('@/views/DataMajorDetailView.vue'),
          meta: { title: '专业研究方向详情表' },
        },
        {
          path: 'university',
          name: 'UniversityDetail',
          component: () => import('@/views/UniversityDetailView.vue'),
          meta: { title: '院校详情' },
        },
        {
          path: 'major-distribution',
          name: 'MajorDistribution',
          component: () => import('@/views/MajorDistributionView.vue'),
          meta: { title: '专业院校分布' },
        },
        {
          path: 'operation-log',
          name: 'OperationLog',
          component: () => import('@/views/OperationLogView.vue'),
          meta: { title: '操作日志' },
        },
      ],
    },
  ],
})

/** 全局前置守卫：未登录用户重定向到登录页 */
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth !== false && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
