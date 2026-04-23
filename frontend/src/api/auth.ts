/**
 * 用户认证相关 API
 */

import request from '@/utils/request'
import type { TokenResponse, UserInfo, UserProfile } from '@/types'

/** 用户注册 */
export function registerApi(data: { username: string; password: string; nickname?: string }) {
  return request.post<TokenResponse>('/auth/register', data)
}

/** 用户登录 */
export function loginApi(data: { username: string; password: string }) {
  return request.post<TokenResponse>('/auth/login', data)
}

/** 获取当前用户信息 */
export function getUserInfoApi() {
  return request.get<UserInfo>('/auth/me')
}

/** 更新用户画像 */
export function updateProfileApi(data: UserProfile) {
  return request.put('/auth/profile', data)
}
