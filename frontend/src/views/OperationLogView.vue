<template>
  <!-- 操作日志页面 -->
  <div class="log-page">
    <el-card shadow="never">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <h3>操作日志</h3>
          <el-select v-model="actionFilter" placeholder="全部操作类型" clearable style="width:160px" @change="handleSearch">
            <el-option v-for="a in actionOptions" :key="a.value" :label="a.label" :value="a.value" />
          </el-select>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" stripe border style="width:100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="action_label" label="操作类型" width="120">
          <template #default="{ row }">
            <el-tag :type="actionTagType(row.action)" size="small">{{ row.action_label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detail" label="操作详情" min-width="300" show-overflow-tooltip>
          <template #default="{ row }">
            {{ formatDetail(row.detail) }}
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="130" />
        <el-table-column prop="created_at" label="操作时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next, jumper"
          @current-change="fetchData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
/**
 * 操作日志页面
 * 展示当前用户的操作记录，支持按操作类型筛选和分页。
 */
import { ref, onMounted } from 'vue'
import { getOperationLogsApi } from '@/api/oplog'

const actionFilter = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)
const loading = ref(false)
const tableData = ref<any[]>([])

const actionOptions = [
  { value: 'login', label: '用户登录' },
  { value: 'search', label: '检索查询' },
  { value: 'recommend', label: '智能推荐' },
  { value: 'favorite_add', label: '添加收藏' },
  { value: 'favorite_remove', label: '取消收藏' },
  { value: 'compare', label: '院校对比' },
  { value: 'export_pdf', label: '导出报告' },
  { value: 'view_detail', label: '查看详情' },
  { value: 'profile_update', label: '更新画像' },
]

onMounted(() => fetchData())

async function fetchData() {
  loading.value = true
  try {
    const res = await getOperationLogsApi({
      action: actionFilter.value || undefined,
      page: page.value,
      page_size: pageSize,
    })
    tableData.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  fetchData()
}

function actionTagType(action: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<string, '' | 'success' | 'warning' | 'danger' | 'info'> = {
    login: 'success', search: '', recommend: 'warning',
    favorite_add: 'success', favorite_remove: 'danger',
    compare: 'info', export_pdf: 'warning', view_detail: 'info',
    profile_update: 'success',
  }
  return map[action] || ''
}

function formatDetail(detail?: string): string {
  if (!detail) return '-'
  try {
    const obj = JSON.parse(detail)
    return Object.entries(obj).map(([k, v]) => `${k}: ${v}`).join(', ')
  } catch {
    return detail
  }
}

function formatDate(dateStr?: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.log-page { display: flex; flex-direction: column; gap: 16px; }
.pagination { margin-top: 16px; display: flex; justify-content: center; }
</style>
