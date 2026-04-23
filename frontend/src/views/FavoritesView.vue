<template>
  <!-- 我的收藏页面 -->
  <div class="favorites-page">
    <el-card shadow="never">
      <template #header>
        <div class="fav-header">
          <h3>我的收藏夹</h3>
          <el-button
            type="primary"
            :disabled="selectedIds.length < 2 || selectedIds.length > 3"
            @click="goCompare"
          >
            <el-icon><DataAnalysis /></el-icon>
            对比选中（{{ selectedIds.length }}）
          </el-button>
        </div>
        <p class="sub-title">勾选 2-3 个院校可进行横向对比</p>
      </template>

      <el-table
        :data="favorites"
        v-loading="loading"
        @selection-change="onSelectionChange"
        style="width: 100%"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="dwmc" label="院校名称" min-width="200" />
        <el-table-column prop="zymc" label="专业名称" min-width="180" />
        <el-table-column prop="dwdm" label="院校代码" width="120" />
        <el-table-column prop="zydm" label="专业代码" width="120" />
        <el-table-column label="收藏时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              type="danger"
              size="small"
              text
              @click="handleRemove(row.id)"
            >
              取消收藏
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && favorites.length === 0" description="暂无收藏" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
/**
 * 我的收藏页面
 * 展示用户收藏的院校列表，支持取消收藏和选择对比。
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataAnalysis } from '@element-plus/icons-vue'
import type { FavoriteItem } from '@/types'
import { getFavoritesApi, removeFavoriteApi } from '@/api/workbench'

const router = useRouter()
const favorites = ref<FavoriteItem[]>([])
const loading = ref(false)
const selectedIds = ref<FavoriteItem[]>([])

/** 加载收藏列表 */
async function loadFavorites() {
  loading.value = true
  try {
    const res = await getFavoritesApi()
    favorites.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(loadFavorites)

/** 表格多选变更 */
function onSelectionChange(rows: FavoriteItem[]) {
  selectedIds.value = rows
}

/** 取消收藏 */
async function handleRemove(id: number) {
  await ElMessageBox.confirm('确定取消收藏吗？', '提示', { type: 'warning' })
  await removeFavoriteApi(id)
  ElMessage.success('已取消收藏')
  loadFavorites()
}

/** 跳转到对比页面 */
function goCompare() {
  const selected = selectedIds.value
  if (selected.length < 2 || selected.length > 3) {
    ElMessage.warning('请选择 2-3 个院校进行对比')
    return
  }

  // 将选中院校的代码和专业代码通过 query 传递
  const dwdmList = selected.map((s) => s.dwdm).join(',')
  const zydm = selected[0].zydm
  router.push({ path: '/compare', query: { dwdm: dwdmList, zydm } })
}

/** 格式化日期 */
function formatDate(dateStr?: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.fav-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sub-title {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}
</style>
