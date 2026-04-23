/**
 * 数据看板相关 API
 */

import request from '@/utils/request'

/** 数据概览 */
export function getOverviewApi() {
  return request.get('/dashboard/overview')
}

/** 各省市院校数量分布 */
export function getProvinceUniversityCountApi() {
  return request.get('/dashboard/province_university_count')
}

/** 重点院校分类占比（双一流/985/211） */
export function getEliteUniversityRatioApi() {
  return request.get('/dashboard/elite_university_ratio')
}

/** 学位类型分布 */
export function getDegreeTypeDistributionApi() {
  return request.get('/dashboard/degree_type_distribution')
}

/** 学习方式分布 */
export function getStudyModeDistributionApi() {
  return request.get('/dashboard/study_mode_distribution')
}

/** 自划线院校招生专业数排名 */
export function getZhxUniversityMajorCountApi() {
  return request.get('/dashboard/zhx_university_major_count')
}

/** 各门类招生方向数量分布 */
export function getCategoryDirectionCountApi() {
  return request.get('/dashboard/category_direction_count')
}

/** 各省市拟招生总人数 */
export function getProvinceEnrollmentApi() {
  return request.get('/dashboard/province_enrollment')
}

/** 院校推免占比排名TOP15 */
export function getUniversityTuimianRatioApi() {
  return request.get('/dashboard/university_tuimian_ratio')
}

/** K-Means 院校竞争力聚类分析 */
export function getUniversityClusterAnalysisApi() {
  return request.get('/dashboard/university_cluster_analysis')
}
