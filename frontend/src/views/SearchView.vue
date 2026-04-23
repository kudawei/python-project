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
            <div class="uni-title-row">
              <h4>{{ item.dwmc }}</h4>
              <el-tag size="small" type="info">{{ item.szss }}</el-tag>
            </div>
            <div class="tags">
              <el-tag v-if="isYes(item.syl)" type="danger" size="small">双一流</el-tag>
              <el-tag v-if="isYes(item.zhx)" type="warning" size="small">自划线</el-tag>
              <el-tag v-if="isYes(item.bs)" type="success" size="small">博士点</el-tag>
              <el-tag v-if="item.xxfs" size="small">{{ formatXxfs(item.xxfs) }}</el-tag>
              <el-tag v-if="isYes(item.tydxs)" type="info" size="small" effect="plain">接收退役士兵</el-tag>
              <el-tag v-if="isYes(item.jsggjh)" type="info" size="small" effect="plain">少数民族骨干</el-tag>
            </div>
            <div class="uni-detail">
              <span class="detail-item"><strong>专业：</strong>{{ item.zymc }}（{{ item.zydm }}）</span>
            </div>
          </div>
          <div class="uni-actions">
            <el-button
              :class="{ 'is-favorited': isFavorited(item) }"
              circle
              @click="handleToggleFavorite(item)"
              :title="isFavorited(item) ? '取消收藏' : '收藏'"
            >
              <el-icon :size="18" :color="isFavorited(item) ? '#f56c6c' : '#c0c4cc'">
                <StarFilled v-if="isFavorited(item)" />
                <Star v-else />
              </el-icon>
            </el-button>
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
 * 收藏按钮支持已收藏/未收藏状态切换。
 */
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Star, StarFilled } from '@element-plus/icons-vue'
import type { CascadeOption, UniversityItem, SearchResponse } from '@/types'
import {
  getCategoriesApi,
  getDisciplinesApi,
  getMajorsApi,
  getProvincesApi,
  searchUniversitiesApi,
} from '@/api/search'
import { addFavoriteApi, removeFavoriteApi, batchCheckFavoritesApi } from '@/api/workbench'

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

// ===== 收藏状态 =====
const favoritedSet = ref<Set<string>>(new Set())

/** 判断字段值是否为"是"（兼容 '是'/'1' 取值） */
function isYes(val?: string): boolean {
  return val === '是' || val === '1'
}

/** 格式化学习方式 */
function formatXxfs(val?: string): string {
  if (val === '1' || val === '全日制') return '全日制'
  if (val === '2' || val === '非全日制') return '非全日制'
  return val || ''
}

/** 检查是否已收藏 */
function isFavorited(item: UniversityItem): boolean {
  return favoritedSet.value.has(item.dwdm || '')
}

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

/** 请求搜索结果（不重置页码） */
async function fetchResults() {
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

  // 批量查询已收藏状态
  try {
    const favRes = await batchCheckFavoritesApi(selectedZydm.value)
    favoritedSet.value = new Set(favRes.data.favorited_dwdm_list)
  } catch {
    favoritedSet.value = new Set()
  }
}

/** 执行搜索（重置到第1页） */
async function handleSearch() {
  if (!selectedZydm.value) {
    ElMessage.warning('请先选择专业')
    return
  }
  searched.value = true
  currentPage.value = 1
  await fetchResults()
}

/** 重置过滤条件 */
function handleReset() {
  filterProvinces.value = []
  filterSyl.value = false
  filterZhx.value = false
  filterBs.value = false
}

/** 分页变更（保持当前筛选条件，切换页码） */
async function handlePageChange(page: number) {
  currentPage.value = page
  await fetchResults()
}

/** 切换收藏状态 */
async function handleToggleFavorite(item: UniversityItem) {
  const dwdm = item.dwdm || ''
  if (isFavorited(item)) {
    // 已收藏 → 取消收藏（需要先查 favorite_id）
    try {
      const { data } = await import('@/api/workbench').then(m => m.checkFavoriteApi(dwdm, item.zydm || ''))
      if (data.favorite_id) {
        await removeFavoriteApi(data.favorite_id)
        favoritedSet.value.delete(dwdm)
        // 触发 Set 的响应式更新
        favoritedSet.value = new Set(favoritedSet.value)
        ElMessage.success('已取消收藏')
      }
    } catch {
      // 错误已在拦截器处理
    }
  } else {
    // 未收藏 → 添加收藏
    try {
      await addFavoriteApi({
        dwdm,
        dwmc: item.dwmc,
        zydm: item.zydm || '',
        zymc: item.zymc,
      })
      favoritedSet.value.add(dwdm)
      favoritedSet.value = new Set(favoritedSet.value)
      ElMessage.success('收藏成功')
    } catch {
      // 错误已在拦截器处理
    }
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
  align-items: flex-start;
  justify-content: space-between;
  padding: 20px 16px;
  border-bottom: 1px solid #ebeef5;
  transition: background-color 0.2s;
}

.university-card:hover {
  background-color: #f5f7fa;
}

.university-card:last-child {
  border-bottom: none;
}

.uni-info {
  flex: 1;
}

.uni-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.uni-info h4 {
  font-size: 17px;
  color: #303133;
  margin: 0;
}

.tags {
  display: flex;
  gap: 6px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.uni-detail {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 13px;
  color: #606266;
}

.detail-item strong {
  color: #303133;
}

.uni-actions {
  flex-shrink: 0;
  margin-left: 16px;
  padding-top: 4px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.is-favorited {
  border-color: #f56c6c !important;
  background-color: #fef0f0 !important;
}
</style>
