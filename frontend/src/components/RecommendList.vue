<template>
  <!-- 推荐结果列表组件（被冲刺/稳妥/保底三个区域复用） -->
  <div v-if="items.length > 0">
    <div
      v-for="(item, index) in items"
      :key="index"
      class="rec-item"
    >
      <div class="rec-info">
        <h4>{{ item.dwmc }}</h4>
        <div class="tags">
          <el-tag v-if="item.syl === '是'" type="danger" size="small">双一流</el-tag>
          <el-tag v-if="item.zhx === '是'" type="warning" size="small">自划线</el-tag>
          <el-tag v-if="item.bs === '是'" type="success" size="small">博士点</el-tag>
          <el-tag size="small">{{ item.szss }}</el-tag>
        </div>
      </div>
      <div class="rec-score">
        <span class="score-label">综合得分</span>
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
 */
import { Star } from '@element-plus/icons-vue'
import type { RecommendItem } from '@/types'

defineProps<{
  items: RecommendItem[]
}>()

const emit = defineEmits<{
  favorite: [item: RecommendItem]
}>()
</script>

<style scoped>
.rec-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.rec-item:last-child {
  border-bottom: none;
}

.rec-info {
  flex: 1;
}

.rec-info h4 {
  font-size: 15px;
  color: #303133;
  margin-bottom: 6px;
}

.tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.rec-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0 24px;
}

.score-label {
  font-size: 12px;
  color: #909399;
}

.score-value {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
}

.rec-action {
  flex-shrink: 0;
}
</style>
