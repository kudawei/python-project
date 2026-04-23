/**
 * 数据看板相关 API
 */

import request from '@/utils/request'

/** 数据概览 */
export function getOverviewApi() {
  return request.get('/dashboard/overview')
}

/** 各门类院校数量分布 */
export function getCategoryUniversityCountApi() {
  return request.get('/dashboard/category_university_count')
}

/** 各省市院校数量分布 */
export function getProvinceUniversityCountApi() {
  return request.get('/dashboard/province_university_count')
}

/** 双一流院校占比 */
export function getSylRatioApi() {
  return request.get('/dashboard/syl_ratio')
}

/** 学位类型分布 */
export function getDegreeTypeDistributionApi() {
  return request.get('/dashboard/degree_type_distribution')
}

/** 学习方式分布 */
export function getStudyModeDistributionApi() {
  return request.get('/dashboard/study_mode_distribution')
}

/** 自划线与非自划线对比 */
export function getZhxComparisonApi() {
  return request.get('/dashboard/zhx_comparison')
}

/** 各门类专业数量 TOP10 */
export function getCategoryMajorTop10Api() {
  return request.get('/dashboard/category_major_top10')
}

/** 博士点院校省市分布 */
export function getBsProvinceDistributionApi() {
  return request.get('/dashboard/bs_province_distribution')
}

/** K-Means 院校竞争力聚类分析 */
export function getUniversityClusterAnalysisApi() {
  return request.get('/dashboard/university_cluster_analysis')
}
