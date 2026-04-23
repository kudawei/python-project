/**
 * 工作台相关 API（收藏、对比）
 */

import request from '@/utils/request'
import type { FavoriteItem, CompareItem } from '@/types'

/** 获取收藏列表 */
export function getFavoritesApi() {
  return request.get<FavoriteItem[]>('/workbench/favorites')
}

/** 添加收藏 */
export function addFavoriteApi(data: { dwdm: string; dwmc?: string; zydm: string; zymc?: string }) {
  return request.post('/workbench/favorites', data)
}

/** 取消收藏 */
export function removeFavoriteApi(favoriteId: number) {
  return request.delete(`/workbench/favorites/${favoriteId}`)
}

/** 检查是否已收藏 */
export function checkFavoriteApi(dwdm: string, zydm: string) {
  return request.get<{ is_favorited: boolean; favorite_id: number | null }>('/workbench/favorites/check', {
    params: { dwdm, zydm },
  })
}

/** 院校横向对比 */
export function compareUniversitiesApi(data: { dwdm_list: string[]; zydm: string }) {
  return request.post<CompareItem[]>('/workbench/compare', data)
}
