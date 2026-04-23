<template>
  <!-- 推荐结果列表组件（被冲刺/稳妥/保底三个区域复用） -->
  <div v-if="items.length > 0">
    <div
      v-for="(item, index) in items"
      :key="index"
      class="rec-item"
    >
      <div class="rec-info">
        <div class="rec-title-row">
          <h4>{{ item.dwmc }}</h4>
          <el-tag size="small" type="info" effect="plain">{{ item.szss }}</el-tag>
        </div>
        <div class="tags">
          <el-tag v-if="isYes(item.syl)" type="danger" size="small">双一流</el-tag>
          <el-tag v-if="isYes(item.zhx)" type="warning" size="small">自划线</el-tag>
          <el-tag v-if="isYes(item.bs)" type="success" size="small">博士点</el-tag>
          <el-tag v-if="item.xxfs" size="small" effect="plain">{{ formatXxfs(item.xxfs) }}</el-tag>
        </div>
        <div class="rec-detail">
          <span v-if="item.dwdm" class="detail-item">院校代码：{{ item.dwdm }}</span>
        </div>
      </div>
      <div class="rec-score">
        <el-tooltip content="综合得分 = 难度系数(自划线+5, 双一流+3, 博士点+1) + 匹配度(省市+10, 学习方式+5)" placement="top">
          <span class="score-label">综合得分 <el-icon :size="12"><QuestionFilled /></el-icon></span>
        </el-tooltip>
        <span class="score-value">{{ item.score }}</span>
      </div>
      <div class="rec-action">
        <el-button
          type="warning"
          :icon="Star"
          circle
          size="small"
          @click="emit('favorite', item)"
          title="收藏"
        />
      </div>
    </div>
  </div>
  <el-empty v-else description="暂无数据" :image-size="60" />
</template>

<script setup lang="ts">
/**
 * 推荐列表子组件
 * 展示单个梯度的推荐院校列表，支持收藏操作。
 * 标签兼容 '是'/'1' 两种取值格式。
 */
import { Star, QuestionFilled } from '@element-plus/icons-vue'
import type { RecommendItem } from '@/types'

defineProps<{
  items: RecommendItem[]
}>()

const emit = defineEmits<{
  favorite: [item: RecommendItem]
}>()

/** 兼容 '是'/'1' 判断 */
function isYes(val?: string): boolean {
  return val === '是' || val === '1'
}

/** 格式化学习方式 */
function formatXxfs(val?: string): string {
  if (val === '1' || val === '全日制') return '全日制'
  if (val === '2' || val === '非全日制') return '非全日制'
  return val || ''
}
</script>

<style scoped>
.rec-item {
  display: flex;
  align-items: flex-start;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.rec-item:hover {
  background-color: #fafafa;
}

.rec-item:last-child {
  border-bottom: none;
}

.rec-info {
  flex: 1;
}

.rec-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.rec-info h4 {
  font-size: 16px;
  color: #303133;
  margin: 0;
}

.tags {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}

.rec-detail {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.rec-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0 24px;
  min-width: 80px;
}

.score-label {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 2px;
  cursor: help;
}

.score-value {
  font-size: 22px;
  font-weight: bold;
  color: #409eff;
}

.rec-action {
  flex-shrink: 0;
  padding-top: 4px;
}
</style>
