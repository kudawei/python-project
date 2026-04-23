<template>
  <!-- 智能推荐页面 -->
  <div class="recommend-page">
    <!-- 专业选择区 -->
    <el-card shadow="never">
      <template #header>
        <h3>智能推荐 — 选择目标专业</h3>
        <p class="sub-title">
          根据您的考研意向画像，系统将为您推荐冲刺、稳妥、保底三个梯度的院校
        </p>
      </template>

      <el-form :inline="true" size="large">
        <el-form-item label="门类">
          <el-select
            v-model="selectedMldm"
            placeholder="选择门类"
            @change="onCategoryChange"
            clearable
            style="width: 180px"
          >
            <el-option
              v-for="item in categories"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="一级学科">
          <el-select
            v-model="selectedYjxkdm"
            placeholder="选择一级学科"
            @change="onDisciplineChange"
            clearable
            :disabled="!selectedMldm"
            style="width: 180px"
          >
            <el-option
              v-for="item in disciplines"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="专业">
          <el-select
            v-model="selectedZydm"
            placeholder="选择专业"
            clearable
            :disabled="!selectedYjxkdm"
            style="width: 180px"
          >
            <el-option
              v-for="item in majors"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleRecommend">
            <el-icon><MagicStick /></el-icon>
            开始推荐
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 推荐结果展示 -->
    <div v-if="hasResult" class="result-section">
      <!-- 冲刺院校 -->
      <el-card shadow="never" class="tier-card tier-sprint">
        <template #header>
          <div class="tier-header">
            <span class="tier-icon">🎯</span>
            <h3>冲刺院校</h3>
            <el-tag type="danger" size="small">{{ result.sprint.length }} 所</el-tag>
          </div>
          <p class="tier-desc">难度系数较高，需要付出更多努力的顶级院校</p>
        </template>
        <recommend-list :items="result.sprint" @favorite="handleFavorite" />
      </el-card>

      <!-- 稳妥院校 -->
      <el-card shadow="never" class="tier-card tier-stable">
        <template #header>
          <div class="tier-header">
            <span class="tier-icon">✅</span>
            <h3>稳妥院校</h3>
            <el-tag type="success" size="small">{{ result.stable.length }} 所</el-tag>
          </div>
          <p class="tier-desc">难度适中，与您的期望高度匹配的院校</p>
        </template>
        <recommend-list :items="result.stable" @favorite="handleFavorite" />
      </el-card>

      <!-- 保底院校 -->
      <el-card shadow="never" class="tier-card tier-safe">
        <template #header>
          <div class="tier-header">
            <span class="tier-icon">🛡️</span>
            <h3>保底院校</h3>
            <el-tag type="info" size="small">{{ result.safe.length }} 所</el-tag>
          </div>
          <p class="tier-desc">难度较低，专业匹配且录取把握较大的院校</p>
        </template>
        <recommend-list :items="result.safe" @favorite="handleFavorite" />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 智能推荐页面
 * 用户选择目标专业后，调用推荐算法接口，展示分梯度的推荐结果。
 */
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick } from '@element-plus/icons-vue'
import type { CascadeOption, RecommendResponse, RecommendItem } from '@/types'
import { getCategoriesApi, getDisciplinesApi, getMajorsApi } from '@/api/search'
import { getRecommendationsApi } from '@/api/recommend'
import { addFavoriteApi } from '@/api/workbench'
import RecommendList from '@/components/RecommendList.vue'

const categories = ref<CascadeOption[]>([])
const disciplines = ref<CascadeOption[]>([])
const majors = ref<CascadeOption[]>([])

const selectedMldm = ref('')
const selectedYjxkdm = ref('')
const selectedZydm = ref('')
const loading = ref(false)
const hasResult = ref(false)

const result = ref<RecommendResponse>({ sprint: [], stable: [], safe: [] })

onMounted(async () => {
  const res = await getCategoriesApi()
  categories.value = res.data
})

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

async function onDisciplineChange(val: string) {
  selectedZydm.value = ''
  majors.value = []
  if (val) {
    const res = await getMajorsApi(val)
    majors.value = res.data
  }
}

/** 执行推荐 */
async function handleRecommend() {
  if (!selectedZydm.value) {
    ElMessage.warning('请先选择目标专业')
    return
  }

  loading.value = true
  try {
    const res = await getRecommendationsApi(selectedZydm.value)
    result.value = res.data
    hasResult.value = true

    if (
      res.data.sprint.length === 0 &&
      res.data.stable.length === 0 &&
      res.data.safe.length === 0
    ) {
      ElMessage.info('该专业暂无可推荐的院校数据')
    }
  } catch {
    // 错误已在拦截器处理
  } finally {
    loading.value = false
  }
}

/** 收藏推荐院校 */
async function handleFavorite(item: RecommendItem) {
  try {
    await addFavoriteApi({
      dwdm: item.dwdm || '',
      dwmc: item.dwmc,
      zydm: selectedZydm.value,
      zymc: '',
    })
    ElMessage.success('收藏成功')
  } catch {
    // 已处理
  }
}
</script>

<style scoped>
.recommend-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sub-title {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.result-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tier-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tier-icon {
  font-size: 20px;
}

.tier-desc {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.tier-sprint :deep(.el-card__header) {
  border-left: 4px solid #f56c6c;
}

.tier-stable :deep(.el-card__header) {
  border-left: 4px solid #67c23a;
}

.tier-safe :deep(.el-card__header) {
  border-left: 4px solid #909399;
}
</style>
