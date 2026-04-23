<template>
  <!-- 支撑数据：专业研究方向详情表 -->
  <div class="data-page">
    <el-card shadow="never">
      <template #header>
        <h3>专业研究方向详情表（major_detail）</h3>
      </template>

      <!-- 筛选区域 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="关键字">
          <el-input v-model="keyword" placeholder="院校/专业/研究方向" clearable @keyup.enter="handleSearch" style="width: 200px" />
        </el-form-item>
        <el-form-item label="省市">
          <el-select v-model="szss" placeholder="全部" clearable filterable style="width: 130px">
            <el-option v-for="p in provinces" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="门类">
          <el-select v-model="mldm" placeholder="全部" clearable style="width: 160px">
            <el-option v-for="c in categories" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="tableData" v-loading="loading" stripe border style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="dwmc" label="院校名称" min-width="170" show-overflow-tooltip />
        <el-table-column prop="szss" label="省市" width="70" />
        <el-table-column prop="zymc" label="专业名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="mlmc" label="门类" width="80" show-overflow-tooltip />
        <el-table-column prop="yxsmc" label="院系所" min-width="150" show-overflow-tooltip />
        <el-table-column prop="yjfxmc" label="研究方向" min-width="150" show-overflow-tooltip />
        <el-table-column prop="zdjs" label="指导教师" width="120" show-overflow-tooltip />
        <el-table-column prop="nzsrs" label="拟招生" width="70" align="center" />
        <el-table-column prop="xxfs" label="学习方式" width="80">
          <template #default="{ row }">
            {{ row.xxfs === '1' ? '全日制' : row.xxfs === '2' ? '非全日制' : row.xxfs || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="双一流" width="65" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.syl === '是' || row.syl === '1'" type="danger" size="small">是</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="985" width="55" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.b985 === '是' || row.b985 === '1'" type="danger" size="small">是</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="211" width="55" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.b211 === '是' || row.b211 === '1'" type="warning" size="small">是</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="考试科目" min-width="220">
          <template #default="{ row }">
            <div class="exam-subjects">
              <span v-if="row.km1mc">①{{ row.km1mc }}</span>
              <span v-if="row.km2mc">②{{ row.km2mc }}</span>
              <span v-if="row.km3mc">③{{ row.km3mc }}</span>
              <span v-if="row.km4mc">④{{ row.km4mc }}</span>
            </div>
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
 * 支撑数据 - 专业研究方向详情表
 * 展示 major_detail 表的全部数据，支持关键字、省市、门类筛选。
 * 含考试科目、指导教师、招生人数等详细信息。
 */
import { ref, onMounted } from 'vue'
import { getMajorDetailListApi, getMajorDetailFiltersApi } from '@/api/data'

const keyword = ref('')
const szss = ref('')
const mldm = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)
const loading = ref(false)
const tableData = ref<any[]>([])
const provinces = ref<{ value: string; label: string }[]>([])
const categories = ref<{ value: string; label: string }[]>([])

onMounted(async () => {
  const filterRes = await getMajorDetailFiltersApi()
  provinces.value = filterRes.data.provinces
  categories.value = filterRes.data.categories
  fetchData()
})

async function fetchData() {
  loading.value = true
  try {
    const res = await getMajorDetailListApi({
      keyword: keyword.value || undefined,
      szss: szss.value || undefined,
      mldm: mldm.value || undefined,
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

function handleReset() {
  keyword.value = ''
  szss.value = ''
  mldm.value = ''
  handleSearch()
}
</script>

<style scoped>
.data-page { display: flex; flex-direction: column; gap: 16px; }
.filter-form { margin-bottom: 16px; }
.pagination { margin-top: 16px; display: flex; justify-content: center; }
.exam-subjects {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
  color: #606266;
}
</style>
