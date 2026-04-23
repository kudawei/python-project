/**
 * 操作日志 API
 */

import request from '@/utils/request'

/** 记录操作日志 */
export function addOperationLogApi(action: string, detail?: string) {
  return request.post('/oplog/log', null, { params: { action, detail } })
}

/** 查询操作日志 */
export function getOperationLogsApi(params: { action?: string; page?: number; page_size?: number }) {
  return request.get('/oplog/logs', { params })
}
