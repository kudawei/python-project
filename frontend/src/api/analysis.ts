/**
 * 数据分析 API
 * 专业院校分布、词云分析、院校对比雷达图。
 */

import request from '@/utils/request'

/** 专业院校省市分布 */
export function getMajorProvinceDistributionApi(zydm: string) {
  return request.get('/analysis/major_province_distribution', { params: { zydm } })
}

/** 研究方向词云 */
export function getWordcloudApi(params: { dwdm?: string; zydm?: string }) {
  return request.get('/analysis/wordcloud', { params })
}

/** 院校对比雷达图数据 */
export function getUniversityRadarApi(dwdmList: string) {
  return request.get('/analysis/university_radar', { params: { dwdm_list: dwdmList } })
}
