/**
 * 检索相关 API
 */

import request from '@/utils/request'
import type { CascadeOption, SearchResponse } from '@/types'

/** 获取门类列表 */
export function getCategoriesApi() {
  return request.get<CascadeOption[]>('/search/categories')
}

/** 获取一级学科列表 */
export function getDisciplinesApi(mldm: string) {
  return request.get<CascadeOption[]>('/search/disciplines', { params: { mldm } })
}

/** 获取专业列表 */
export function getMajorsApi(yjxkdm: string) {
  return request.get<CascadeOption[]>('/search/majors', { params: { yjxkdm } })
}

/** 获取省市列表 */
export function getProvincesApi() {
  return request.get<CascadeOption[]>('/search/provinces')
}

/** 高级检索院校列表 */
export function searchUniversitiesApi(params: {
  zydm: string
  szss?: string
  syl?: boolean
  zhx?: boolean
  bs?: boolean
  xxfs?: string
  page?: number
  page_size?: number
}) {
  return request.get<SearchResponse>('/search/universities', { params })
}
