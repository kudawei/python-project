/**
 * 考研择校报告 API
 */

import request from '@/utils/request'

/** 生成并下载 PDF 报告 */
export function generateReportApi(zydm: string) {
  return request.post('/report/generate', null, {
    params: { zydm },
    responseType: 'blob',
  })
}
