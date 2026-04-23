/**
 * 支撑数据浏览 API
 * 提供 major / major_university / major_detail 三张表的分页查询和筛选选项。
 */

import request from '@/utils/request'

/** 通用分页查询参数 */
interface PageParams {
  keyword?: string
  mldm?: string
  szss?: string
  xwlx?: string
  page?: number
  page_size?: number
}

/** 查询专业信息表 */
export function getMajorListApi(params: PageParams) {
  return request.get('/data/major', { params })
}

/** 获取专业表筛选选项 */
export function getMajorFiltersApi() {
  return request.get('/data/major/filters')
}

/** 查询专业-院校关联表 */
export function getMajorUniversityListApi(params: PageParams) {
  return request.get('/data/major_university', { params })
}

/** 获取关联表筛选选项 */
export function getMajorUniversityFiltersApi() {
  return request.get('/data/major_university/filters')
}

/** 查询专业研究方向详情表 */
export function getMajorDetailListApi(params: PageParams) {
  return request.get('/data/major_detail', { params })
}

/** 获取详情表筛选选项 */
export function getMajorDetailFiltersApi() {
  return request.get('/data/major_detail/filters')
}
