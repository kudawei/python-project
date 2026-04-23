<template>
  <!-- 多维检索页面 -->
  <div class="search-page">
    <!-- 级联筛选器卡片 -->
    <el-card shadow="never" class="filter-card">
      <template #header>
        <h3>专业级联筛选</h3>
      </template>

      <el-form :inline="true" size="large">
        <!-- 第一级：门类选择 -->
        <el-form-item label="门类">
          <el-select
            v-model="selectedMldm"
            placeholder="请选择门类"
            @change="onCategoryChange"
            clearable
            style="width: 200px"
          >
            <el-option
              v-for="item in categories"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <!-- 第二级：一级学科选择 -->
        <el-form-item label="一级学科">
          <el-select
            v-model="selectedYjxkdm"
            placeholder="请选择一级学科"
            @change="onDisciplineChange"
            clearable
            :disabled="!selectedMldm"
            style="width: 200px"
          >
            <el-option
              v-for="item in disciplines"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <!-- 第三级：专业选择 -->
        <el-form-item label="专业">
          <el-select
            v-model="selectedZydm"
            placeholder="请选择专业"
            clearable
            :disabled="!selectedYjxkdm"
            style="width: 200px"
          >
            <el-option
              v-for="item in majors"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 高级过滤面板 -->
    <el-card shadow="never" class="filter-card" v-if="selectedZydm">
      <template #header>
        <h3>高级过滤条件</h3>
      </template>

      <el-form :inline="true">
        <!-- 省市过滤 -->
        <el-form-item label="目标省市">
          <el-select
            v-model="filterProvinces"
            multiple
            placeholder="选择省市"
            clearable
            collapse-tags
            collapse-tags-tooltip
            style="width: 260px"
          >
            <el-option
              v-for="item in provinces"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <!-- 特性复选框过滤 -->
        <el-form-item label="院校特性">
          <el-checkbox v-model="filterSyl">仅看双一流</el-checkbox>
          <el-checkbox v-model="filterZhx">仅看自划线</el-checkbox>
          <el-checkbox v-model="filterBs">仅看有博士点</el-checkbox>
        </el-form-item>

        <!-- 搜索按钮 -->
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 检索结果列表 -->
    <el-card shadow="never" v-if="searchResult.items.length > 0 || searched">
      <template #header>
        <div class="result-header">
          <h3>检索结果</h3>
          <span class="total">共 {{ searchResult.total }} 条</span>
        </div>
      </template>

      <!-- 院校卡片列表 -->
      <div v-if="searchResult.items.length > 0">
        <div
          v-for="item in searchResult.items"
          :key="item.id"
          class="university-card"
        >
          <div class="uni-info">
            <h4>{{ item.dwmc }}</h4>
            <div class="tags">
              <el-tag v-if="item.syl === '是'" type="danger" size="small">双一流</el-tag>
              <el-tag v-if="item.zhx === '是'" type="warning" size="small">自划线</el-tag>
              <el-tag v-if="item.bs === '是'" type="success" size="small">博士点</el-tag>
              <el-tag size="small">{{ item.szss }}</el-tag>
              <el-tag type="info" size="small">{{ item.xxfs }}</el-tag>
            </div>
            <p class="meta">
              专业：{{ item.zymc }}（{{ item.zydm }}）
            </p>
          </div>
          <div class="uni-actions">
            <el-button
              type="warning"
              :icon="Star"
              circle
              @click="handleFavorite(item)"
              title="收藏"
            />
          </div>
        </div>
      </div>

      <el-empty v-else description="暂无匹配结果" />

      <!-- 分页器 -->
      <div class="pagination" v-if="searchResult.total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="searchResult.total"
          layout="prev, pager, next, jumper, total"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
/**
 * 多维检索页面
 * 实现门类 → 一级学科 → 专业三级级联筛选，以及高级过滤面板。
 */
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Star } from '@element-plus/icons-vue'
import type { CascadeOption, UniversityItem, SearchResponse } from '@/types'
import {
  getCategoriesApi,
  getDisciplinesApi,
  getMajorsApi,
  getProvincesApi,
  searchUniversitiesApi,
} from '@/api/search'
import { addFavoriteApi } from '@/api/workbench'

// ===== 级联选择器状态 =====
const categories = ref<CascadeOption[]>([])
const disciplines = ref<CascadeOption[]>([])
const majors = ref<CascadeOption[]>([])
const provinces = ref<CascadeOption[]>([])

const selectedMldm = ref('')
const selectedYjxkdm = ref('')
const selectedZydm = ref('')

// ===== 高级过滤条件 =====
const filterProvinces = ref<string[]>([])
const filterSyl = ref(false)
const filterZhx = ref(false)
const filterBs = ref(false)

// ===== 搜索结果与分页 =====
const searched = ref(false)
const searchResult = ref<SearchResponse>({ total: 0, page: 1, page_size: 10, items: [] })
const currentPage = ref(1)
const pageSize = 10

/** 页面加载时获取门类和省市列表 */
onMounted(async () => {
  const [catRes, provRes] = await Promise.all([
    getCategoriesApi(),
    getProvincesApi(),
  ])
  categories.value = catRes.data
  provinces.value = provRes.data
})

/** 门类变更：清空下级并加载一级学科 */
async function onCategoryChange(val: string) {
  selectedYjxkdm.value = ''
  selectedZydm.value = ''
  disciplines.value = []
  majors.value = []
  if (val) {
    const res = await getDisciplinesApi(val)
    disciplines.value = res.data
  }
}

/** 一级学科变更：清空专业并加载专业列表 */
async function onDisciplineChange(val: string) {
  selectedZydm.value = ''
  majors.value = []
  if (val) {
    const res = await getMajorsApi(val)
    majors.value = res.data
  }
}

/** 执行搜索 */
async function handleSearch() {
  if (!selectedZydm.value) {
    ElMessage.warning('请先选择专业')
    return
  }

  searched.value = true
  currentPage.value = 1

  const res = await searchUniversitiesApi({
    zydm: selectedZydm.value,
    szss: filterProvinces.value.length > 0 ? filterProvinces.value.join(',') : undefined,
    syl: filterSyl.value || undefined,
    zhx: filterZhx.value || undefined,
    bs: filterBs.value || undefined,
    page: currentPage.value,
    page_size: pageSize,
  })
  searchResult.value = res.data
}

/** 重置过滤条件 */
function handleReset() {
  filterProvinces.value = []
  filterSyl.value = false
  filterZhx.value = false
  filterBs.value = false
}

/** 分页变更 */
async function handlePageChange(page: number) {
  currentPage.value = page
  await handleSearch()
}

/** 收藏院校 */
async function handleFavorite(item: UniversityItem) {
  try {
    await addFavoriteApi({
      dwdm: item.dwdm || '',
      dwmc: item.dwmc,
      zydm: item.zydm || '',
      zymc: item.zymc,
    })
    ElMessage.success('收藏成功')
  } catch {
    // 错误已在拦截器处理（如已收藏会提示）
  }
}
</script>

<style scoped>
.search-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-card {
  margin-bottom: 0;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.total {
  font-size: 14px;
  color: #909399;
}

.university-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
}

.university-card:last-child {
  border-bottom: none;
}

.uni-info h4 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 8px;
}

.tags {
  display: flex;
  gap: 6px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.meta {
  font-size: 13px;
  color: #909399;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
