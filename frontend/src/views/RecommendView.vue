<template>
  <!-- 智能推荐页面 -->
  <div class="recommend-page">
    <!-- 专业选择区 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header-row">
          <div>
            <h3>智能推荐 — 选择目标专业</h3>
            <p class="sub-title">
              根据您的考研意向画像，系统将为您推荐冲刺、稳妥、保底三个梯度的院校
            </p>
          </div>
          <el-tooltip v-if="profileLoaded" placement="bottom">
            <template #content>
              <div style="line-height: 1.8; font-size: 13px;">
                <p><strong>综合得分 = 难度系数 + 匹配度得分</strong></p>
                <p>【难度系数】</p>
                <p>自划线院校 +5 分 | 双一流院校 +3 分 | 博士点 +1 分</p>
                <p>【匹配度得分】</p>
                <p>院校省市匹配意向省市 +10 分 | 学习方式匹配 +5 分</p>
                <p>【梯度划分规则】</p>
                <p>根据"实力自评"设定难度阈值，高于阈值 → 冲刺，中间 → 稳妥，低于 → 保底</p>
              </div>
            </template>
            <el-button :icon="QuestionFilled" circle size="small" text />
          </el-tooltip>
        </div>
      </template>

      <!-- 用户画像已加载时直接展示画像摘要 -->
      <div v-if="profileLoaded" class="profile-summary">
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="意向门类">{{ userStore.userInfo?.target_mlmc || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="意向省市">{{ profileProvincesText }}</el-descriptions-item>
          <el-descriptions-item label="学位期望">{{ profileDegreeText }}</el-descriptions-item>
          <el-descriptions-item label="学习方式">{{ profileStudyText }}</el-descriptions-item>
          <el-descriptions-item label="实力自评">{{ profileRatingText }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <el-form :inline="true" size="large" style="margin-top: 16px;">
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
            <span class="tier-icon">🏅</span>
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
 * 已完成画像的用户，自动加载画像的意向门类作为默认选项；
 * 用户选择目标专业后，调用推荐算法接口，展示分梯度的推荐结果。
 */
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick, QuestionFilled } from '@element-plus/icons-vue'
import type { CascadeOption, RecommendResponse, RecommendItem } from '@/types'
import { getCategoriesApi, getDisciplinesApi, getMajorsApi } from '@/api/search'
import { getRecommendationsApi } from '@/api/recommend'
import { addFavoriteApi } from '@/api/workbench'
import { useUserStore } from '@/stores/user'
import RecommendList from '@/components/RecommendList.vue'

const userStore = useUserStore()

const categories = ref<CascadeOption[]>([])
const disciplines = ref<CascadeOption[]>([])
const majors = ref<CascadeOption[]>([])

const selectedMldm = ref('')
const selectedYjxkdm = ref('')
const selectedZydm = ref('')
const loading = ref(false)
const hasResult = ref(false)
const profileLoaded = ref(false)

const result = ref<RecommendResponse>({ sprint: [], stable: [], safe: [] })

// 画像信息展示
const profileProvincesText = computed(() => {
  const p = userStore.userInfo?.target_provinces
  return p && p.length > 0 ? p.join('、') : '未设置'
})

const profileDegreeText = computed(() => {
  const d = userStore.userInfo?.degree_type
  if (d === 'xs') return '学术学位'
  if (d === 'zy') return '专业学位'
  return d || '未设置'
})

const profileStudyText = computed(() => {
  const s = userStore.userInfo?.study_mode
  if (s === '1' || s === '全日制') return '全日制'
  if (s === '2' || s === '非全日制') return '非全日制'
  return s || '未设置'
})

const profileRatingText = computed(() => {
  const r = userStore.userInfo?.self_rating
  if (r === 'strong') return '强'
  if (r === 'medium') return '中等'
  if (r === 'weak') return '弱'
  return r || '未设置'
})

onMounted(async () => {
  // 确保用户信息已加载
  if (!userStore.userInfo) {
    await userStore.fetchUserInfo()
  }

  const catRes = await getCategoriesApi()
  categories.value = catRes.data

  // 如果用户已完成画像且有意向门类，自动填充门类选择
  if (userStore.userInfo?.profile_completed === 1 && userStore.userInfo.target_mldm) {
    profileLoaded.value = true
    const mldm = userStore.userInfo.target_mldm
    selectedMldm.value = mldm
    // 自动加载对应的一级学科
    const discRes = await getDisciplinesApi(mldm)
    disciplines.value = discRes.data
  } else {
    profileLoaded.value = true
  }
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
      dwmc: item.dwmc || '',
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

.card-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.sub-title {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.profile-summary {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
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
