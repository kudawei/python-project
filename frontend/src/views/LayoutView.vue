<template>
  <!-- 主布局：左侧菜单 + 顶部导航 + 内容区 -->
  <el-container class="layout-container">
    <!-- 左侧菜单栏 -->
    <el-aside width="220px" class="aside">
      <div class="logo">
        <el-icon :size="24"><School /></el-icon>
        <span>考研推荐系统</span>
      </div>
      <el-menu
        :default-active="route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>数据看板</span>
        </el-menu-item>
        <el-menu-item index="/search">
          <el-icon><Search /></el-icon>
          <span>多维检索</span>
        </el-menu-item>
        <el-menu-item index="/recommend">
          <el-icon><MagicStick /></el-icon>
          <span>智能推荐</span>
        </el-menu-item>
        <el-menu-item index="/favorites">
          <el-icon><Star /></el-icon>
          <span>我的收藏</span>
        </el-menu-item>
        <el-menu-item index="/recommend-history">
          <el-icon><Clock /></el-icon>
          <span>推荐历史</span>
        </el-menu-item>
        <el-menu-item index="/compare">
          <el-icon><DataAnalysis /></el-icon>
          <span>院校对比</span>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span>考研画像</span>
        </el-menu-item>
        <el-sub-menu index="data">
          <template #title>
            <el-icon><FolderOpened /></el-icon>
            <span>支撑数据</span>
          </template>
          <el-menu-item index="/data/major">专业信息表</el-menu-item>
          <el-menu-item index="/data/major-university">专业-院校关联表</el-menu-item>
          <el-menu-item index="/data/major-detail">研究方向详情表</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- 右侧内容区 -->
    <el-container>
      <!-- 顶部栏 -->
      <el-header class="header">
        <span class="page-title">{{ route.meta.title }}</span>
        <div class="user-area">
          <el-dropdown @command="handleCommand">
            <span class="user-name">
              {{ userStore.userInfo?.nickname || userStore.userInfo?.username || '用户' }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
/**
 * 主布局组件
 * 包含左侧导航菜单、顶部用户信息栏和内容区。
 */
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Search,
  MagicStick,
  Star,
  DataAnalysis,
  User,
  ArrowDown,
  School,
  DataBoard,
  FolderOpened,
  Clock,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

/** 页面加载时获取用户信息 */
onMounted(() => {
  if (userStore.isLoggedIn && !userStore.userInfo) {
    userStore.fetchUserInfo()
  }
})

/** 下拉菜单命令处理 */
function handleCommand(command: string) {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.aside {
  background-color: #304156;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  border-bottom: 1px solid #3a4a5c;
}

.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  padding: 0 20px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.user-area {
  display: flex;
  align-items: center;
}

.user-name {
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #606266;
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>
