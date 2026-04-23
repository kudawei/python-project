/**
 * 院校画像 API
 */

import request from '@/utils/request'

/** 院校基本信息 */
export function getUniversityDetailApi(dwdm: string) {
  return request.get('/university/detail', { params: { dwdm } })
}

/** 统考与推免比例饼图 */
export function getEnrollmentPieApi(dwdm: string) {
  return request.get('/university/enrollment_pie', { params: { dwdm } })
}

/** 院系招生分布 */
export function getDepartmentBarApi(dwdm: string) {
  return request.get('/university/department_bar', { params: { dwdm } })
}

/** 学习方式分布 */
export function getStudyModePieApi(dwdm: string) {
  return request.get('/university/study_mode_pie', { params: { dwdm } })
}

/** 该校专业研究方向列表 */
export function getUniversityProgramsApi(params: { dwdm: string; keyword?: string; page?: number; page_size?: number }) {
  return request.get('/university/programs', { params })
}
