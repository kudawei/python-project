/**
 * 智能推荐相关 API
 */

import request from '@/utils/request'
import type { RecommendResponse } from '@/types'

/** 获取智能推荐结果 */
export function getRecommendationsApi(zydm: string) {
  return request.post<RecommendResponse>('/recommend/', { zydm })
}

/** 获取推荐历史记录 */
export function getRecommendHistoryApi(params: { page?: number; page_size?: number }) {
  return request.get('/recommend/history', { params })
}

/** 获取推荐历史统计摘要 */
export function getRecommendSummaryApi() {
  return request.get('/recommend/history/summary')
}
