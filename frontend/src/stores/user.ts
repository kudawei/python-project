/**
 * 用户状态管理 (Pinia Store)
 * 管理用户登录状态、Token、用户信息和画像数据。
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/types'
import { getUserInfoApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  /** JWT Token */
  const token = ref<string>(localStorage.getItem('token') || '')

  /** 用户信息 */
  const userInfo = ref<UserInfo | null>(null)

  /** 是否已登录 */
  const isLoggedIn = computed(() => !!token.value)

  /** 画像是否已完成 */
  const isProfileCompleted = computed(() => userInfo.value?.profile_completed === 1)

  /** 设置 Token（登录/注册成功后调用） */
  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  /** 获取并缓存用户信息 */
  async function fetchUserInfo() {
    try {
      const res = await getUserInfoApi()
      userInfo.value = res.data
    } catch {
      userInfo.value = null
    }
  }

  /** 退出登录 */
  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    isProfileCompleted,
    setToken,
    fetchUserInfo,
    logout,
  }
})
