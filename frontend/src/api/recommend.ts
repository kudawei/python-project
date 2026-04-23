/**
 * 智能推荐相关 API
 */

import request from '@/utils/request'
import type { RecommendResponse } from '@/types'

/** 获取智能推荐结果 */
export function getRecommendationsApi(zydm: string) {
  return request.post<RecommendResponse>('/recommend/', { zydm })
}
