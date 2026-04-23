<template>
  <!-- 支撑数据：专业信息表 -->
  <div class="data-page">
    <el-card shadow="never">
      <template #header>
        <h3>专业信息表（major）</h3>
      </template>

      <!-- 筛选区域 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="关键字">
          <el-input v-model="keyword" placeholder="专业名称/代码" clearable @keyup.enter="handleSearch" style="width: 200px" />
        </el-form-item>
        <el-form-item label="门类">
          <el-select v-model="mldm" placeholder="全部" clearable style="width: 160px">
            <el-option v-for="c in categories" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="学位类型">
          <el-select v-model="xwlx" placeholder="全部" clearable style="width: 120px">
            <el-option label="学术学位" value="xs" />
            <el-option label="专业学位" value="zy" />
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
        <el-table-column prop="zydm" label="专业代码" width="110" />
        <el-table-column prop="zymc" label="专业名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="mldm" label="门类代码" width="90" />
        <el-table-column prop="mlmc" label="门类名称" width="120" show-overflow-tooltip />
        <el-table-column prop="yjxkdm" label="一级学科代码" width="120" />
        <el-table-column prop="yjxkmc" label="一级学科名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="xwlx" label="学位类型" width="90">
          <template #default="{ row }">
            {{ row.xwlx === 'xs' ? '学术' : row.xwlx === 'zy' ? '专业' : row.xwlx }}
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
 * 支撑数据 - 专业信息表
 * 展示 major 表的全部数据，支持关键字、门类、学位类型筛选。
 */
import { ref, onMounted } from 'vue'
import { getMajorListApi, getMajorFiltersApi } from '@/api/data'

const keyword = ref('')
const mldm = ref('')
const xwlx = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)
const loading = ref(false)
const tableData = ref<any[]>([])
const categories = ref<{ value: string; label: string }[]>([])

onMounted(async () => {
  const filterRes = await getMajorFiltersApi()
  categories.value = filterRes.data.categories
  fetchData()
})

async function fetchData() {
  loading.value = true
  try {
    const res = await getMajorListApi({
      keyword: keyword.value || undefined,
      mldm: mldm.value || undefined,
      xwlx: xwlx.value || undefined,
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
  mldm.value = ''
  xwlx.value = ''
  handleSearch()
}
</script>

<style scoped>
.data-page { display: flex; flex-direction: column; gap: 16px; }
.filter-form { margin-bottom: 16px; }
.pagination { margin-top: 16px; display: flex; justify-content: center; }
</style>
