<template>
  <!-- 院校横向对比页面 -->
  <div class="compare-page">
    <el-card shadow="never">
      <template #header>
        <h3>院校PK — 横向对比</h3>
        <p class="sub-title">
          横向比较不同院校在同一专业下的详细属性差异
        </p>
      </template>

      <div v-if="compareData.length > 0" class="compare-table">
        <el-table :data="tableRows" border style="width: 100%">
          <el-table-column prop="label" label="对比项" width="150" fixed />
          <el-table-column
            v-for="(item, idx) in compareData"
            :key="idx"
            :label="item.dwmc || `院校${idx + 1}`"
            min-width="200"
          >
            <template #default="{ row }">
              <span
                :class="{
                  'tag-yes': row.values[idx] === '是',
                  'tag-no': row.values[idx] === '否',
                }"
              >
                {{ row.values[idx] || '-' }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <el-empty
        v-else-if="!loading"
        description="请从收藏夹选择 2-3 个院校进行对比"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
/**
 * 院校横向对比页面
 * 接收从收藏页传入的院校代码，调用对比接口，以表格形式展示属性差异。
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import type { CompareItem } from '@/types'
import { compareUniversitiesApi } from '@/api/workbench'

const route = useRoute()
const compareData = ref<CompareItem[]>([])
const loading = ref(false)

/** 将对比数据转置为行列结构，方便 el-table 渲染 */
const tableRows = computed(() => {
  if (compareData.value.length === 0) return []

  // 定义需要对比的属性及其中文标签
  const fields: { key: keyof CompareItem; label: string }[] = [
    { key: 'dwdm', label: '院校代码' },
    { key: 'szss', label: '所在省市' },
    { key: 'syl', label: '双一流' },
    { key: 'zhx', label: '自划线' },
    { key: 'bs', label: '博士点' },
    { key: 'b985', label: '985工程' },
    { key: 'b211', label: '211工程' },
    { key: 'yjsy', label: '研究生院' },
    { key: 'xxfs', label: '学习方式' },
    { key: 'tydxs', label: '退役士兵计划' },
    { key: 'jsggjh', label: '少骨计划' },
    { key: 'zymc', label: '专业名称' },
    { key: 'yxsmc', label: '院系所' },
    { key: 'yjfxmc', label: '研究方向' },
    { key: 'zdjs', label: '指导教师' },
    { key: 'nzsrs', label: '拟招生人数' },
    { key: 'km1mc', label: '考试科目1' },
    { key: 'km2mc', label: '考试科目2' },
    { key: 'km3mc', label: '考试科目3' },
    { key: 'km4mc', label: '考试科目4' },
  ]

  return fields.map((f) => ({
    label: f.label,
    values: compareData.value.map((item) => {
      const val = item[f.key]
      return val !== null && val !== undefined ? String(val) : '-'
    }),
  }))
})

onMounted(async () => {
  const dwdmStr = route.query.dwdm as string
  const zydm = route.query.zydm as string

  if (!dwdmStr || !zydm) return

  const dwdmList = dwdmStr.split(',')
  loading.value = true
  try {
    const res = await compareUniversitiesApi({ dwdm_list: dwdmList, zydm })
    compareData.value = res.data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.compare-page {
  max-width: 1200px;
}

.sub-title {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.compare-table {
  margin-top: 8px;
}

.tag-yes {
  color: #67c23a;
  font-weight: bold;
}

.tag-no {
  color: #f56c6c;
}
</style>
