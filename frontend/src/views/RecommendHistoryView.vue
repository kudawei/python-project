<template>
  <!-- 推荐历史页面 -->
  <div class="history-page">
    <!-- 统计摘要卡片 -->
    <div class="summary-row">
      <el-card shadow="never" class="summary-card">
        <div class="summary-num">{{ summary.total_records }}</div>
        <div class="summary-label">推荐总次数</div>
      </el-card>
      <el-card shadow="never" class="summary-card">
        <div class="summary-num" style="color: #67c23a;">{{ summary.total_majors }}</div>
        <div class="summary-label">涉及专业数</div>
      </el-card>
      <el-card shadow="never" class="summary-card">
        <div class="summary-num" style="color: #e6a23c;">{{ summary.total_universities }}</div>
        <div class="summary-label">涉及院校数</div>
      </el-card>
    </div>

    <!-- 历史记录表格 -->
    <el-card shadow="never">
      <template #header>
        <h3>推荐历史记录</h3>
      </template>

      <el-table :data="tableData" v-loading="loading" stripe border style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="dwmc" label="推荐院校" min-width="200" show-overflow-tooltip />
        <el-table-column prop="dwdm" label="院校代码" width="100" />
        <el-table-column prop="zydm" label="专业代码" width="100" />
        <el-table-column prop="score" label="综合得分" width="100" align="center">
          <template #default="{ row }">
            <span class="score-val">{{ row.score }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="tier_label" label="推荐梯度" width="110" align="center">
          <template #default="{ row }">
            <el-tag
              :type="tierTagType(row.tier)"
              size="small"
            >
              {{ row.tier_label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="推荐时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
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
 * 推荐历史页面
 * 展示当前用户的所有推荐记录，含统计摘要和分页表格。
 */
import { ref, onMounted } from 'vue'
import { getRecommendHistoryApi, getRecommendSummaryApi } from '@/api/recommend'

const page = ref(1)
const pageSize = 20
const total = ref(0)
const loading = ref(false)
const tableData = ref<any[]>([])
const summary = ref({ total_records: 0, total_majors: 0, total_universities: 0 })

onMounted(async () => {
  const summaryRes = await getRecommendSummaryApi()
  summary.value = summaryRes.data
  fetchData()
})

async function fetchData() {
  loading.value = true
  try {
    const res = await getRecommendHistoryApi({ page: page.value, page_size: pageSize })
    tableData.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

/** 梯度标签颜色 */
function tierTagType(tier: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  if (tier === 'sprint') return 'danger'
  if (tier === 'stable') return 'success'
  if (tier === 'safe') return 'info'
  return ''
}

/** 格式化日期 */
function formatDate(dateStr?: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.history-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.summary-row {
  display: flex;
  gap: 16px;
}

.summary-card {
  flex: 1;
  text-align: center;
}

.summary-num {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
}

.summary-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.score-val {
  font-weight: bold;
  color: #409eff;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}
</style>
