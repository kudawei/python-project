<template>
  <!-- 院校横向对比页面 -->
  <div class="compare-page" v-loading="loading">
    <el-card shadow="never">
      <template #header>
        <h3>院校PK — 横向对比</h3>
        <p class="sub-title">横向比较不同院校在同一专业下的详细属性差异</p>
      </template>

      <!-- 雷达图可视化对比 -->
      <div v-if="radarOption && compareData.length > 0" class="radar-section">
        <h4>综合实力雷达图</h4>
        <v-chart :option="radarOption" style="height: 400px" autoresize />
      </div>

      <!-- 表格对比 -->
      <div v-if="compareData.length > 0" class="compare-table">
        <h4>详细属性对比</h4>
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
                  'tag-yes': row.values[idx] === '是' || row.values[idx] === '1',
                  'tag-no': row.values[idx] === '否' || row.values[idx] === '0',
                }"
              >
                {{ formatCellValue(row.label, row.values[idx]) }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <el-empty v-else-if="!loading" description="请从收藏夹选择 2-3 个院校进行对比" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
/**
 * 院校横向对比页面
 * 接收从收藏页传入的院校代码，展示雷达图可视化对比 + 表格属性差异。
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import VChart from 'vue-echarts'
import type { CompareItem } from '@/types'
import { compareUniversitiesApi } from '@/api/workbench'
import { getUniversityRadarApi } from '@/api/analysis'

const route = useRoute()
const compareData = ref<CompareItem[]>([])
const loading = ref(false)
const radarOption = ref<any>(null)

// 雷达图配色
const radarColors = ['#5470c6', '#91cc75', '#ee6666', '#fac858']

/** 将对比数据转置为行列结构 */
const tableRows = computed(() => {
  if (compareData.value.length === 0) return []

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

/** 格式化单元格值：布尔字段显示中文，学习方式映射 */
function formatCellValue(label: string, val: string): string {
  if (val === '-') return '-'
  const boolLabels = ['双一流', '自划线', '博士点', '985工程', '211工程', '研究生院', '退役士兵计划', '少骨计划']
  if (boolLabels.includes(label)) {
    if (val === '1' || val === '是') return '是'
    if (val === '0' || val === '否') return '否'
  }
  if (label === '学习方式') {
    if (val === '1') return '全日制'
    if (val === '2') return '非全日制'
  }
  return val
}

onMounted(async () => {
  const dwdmStr = route.query.dwdm as string
  const zydm = route.query.zydm as string
  if (!dwdmStr || !zydm) return

  const dwdmList = dwdmStr.split(',')
  loading.value = true
  try {
    // 并行请求对比数据和雷达图数据
    const [compareRes, radarRes] = await Promise.all([
      compareUniversitiesApi({ dwdm_list: dwdmList, zydm }),
      getUniversityRadarApi(dwdmStr),
    ])

    compareData.value = compareRes.data

    // 构建雷达图
    const radar = radarRes.data
    if (radar.universities && radar.universities.length > 0) {
      radarOption.value = {
        tooltip: {},
        legend: {
          bottom: 0,
          data: radar.universities.map((u: any) => u.dwmc),
        },
        radar: {
          indicator: radar.indicators,
          shape: 'polygon',
          radius: '65%',
        },
        series: [{
          type: 'radar',
          data: radar.universities.map((u: any, i: number) => ({
            name: u.dwmc,
            value: u.values,
            lineStyle: { color: radarColors[i % radarColors.length] },
            areaStyle: { color: radarColors[i % radarColors.length], opacity: 0.15 },
            itemStyle: { color: radarColors[i % radarColors.length] },
          })),
        }],
      }
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.compare-page { max-width: 1200px; }
.sub-title { font-size: 13px; color: #909399; margin-top: 4px; }
.radar-section { margin-bottom: 24px; }
.compare-table { margin-top: 8px; }
.tag-yes { color: #67c23a; font-weight: bold; }
.tag-no { color: #f56c6c; }
</style>
