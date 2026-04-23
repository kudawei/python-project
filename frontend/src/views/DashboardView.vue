<template>
  <!-- 数据看板页面 —— 包含 9 个统计图表，支持全屏切换 -->
  <div :class="['dashboard-page', { 'is-fullscreen': isFullscreen }]" ref="dashboardRef" v-loading="loading">

    <!-- 顶部操作栏 -->
    <div class="dashboard-toolbar">
      <h3>数据看板</h3>
      <el-button :icon="isFullscreen ? 'CloseBold' : 'FullScreen'" @click="toggleFullscreen" size="small">
        {{ isFullscreen ? '退出全屏' : '全屏展示' }}
      </el-button>
    </div>

    <!-- 顶部概览卡片 -->
    <div class="overview-row">
      <el-card v-for="card in overviewCards" :key="card.label" shadow="hover" class="overview-card">
        <div class="overview-value" :style="{ color: card.color }">{{ card.value.toLocaleString() }}</div>
        <div class="overview-label">{{ card.label }}</div>
      </el-card>
    </div>

    <!-- 第一行：省市院校分布 + 重点院校数量对比 -->
    <div class="chart-row">
      <el-card shadow="never" class="chart-card">
        <template #header><h4>各省市院校数量分布</h4></template>
        <v-chart :option="provinceUniOption" autoresize class="chart" />
      </el-card>
      <el-card shadow="never" class="chart-card">
        <template #header><h4>重点院校数量对比</h4></template>
        <v-chart :option="eliteRatioOption" autoresize class="chart" />
      </el-card>
    </div>

    <!-- 第二行：学位类型 + 学习方式 -->
    <div class="chart-row">
      <el-card shadow="never" class="chart-card">
        <template #header><h4>学位类型分布</h4></template>
        <v-chart :option="degreeTypeOption" autoresize class="chart" />
      </el-card>
      <el-card shadow="never" class="chart-card">
        <template #header><h4>学习方式分布</h4></template>
        <v-chart :option="studyModeOption" autoresize class="chart" />
      </el-card>
    </div>

    <!-- 第三行：门类招生方向 + 自划线院校专业数 TOP15 -->
    <div class="chart-row">
      <el-card shadow="never" class="chart-card">
        <template #header><h4>各门类招生方向数量分布</h4></template>
        <v-chart :option="categoryDirOption" autoresize class="chart" />
      </el-card>
      <el-card shadow="never" class="chart-card">
        <template #header><h4>自划线院校招生专业数 TOP15</h4></template>
        <v-chart :option="zhxMajorOption" autoresize class="chart" />
      </el-card>
    </div>

    <!-- 第四行：省市招生人数 + 推免占比 TOP15 -->
    <div class="chart-row">
      <el-card shadow="never" class="chart-card">
        <template #header><h4>各省市拟招生总人数</h4></template>
        <v-chart :option="provinceEnrollOption" autoresize class="chart" />
      </el-card>
      <el-card shadow="never" class="chart-card">
        <template #header><h4>院校推免占比 TOP15</h4></template>
        <v-chart :option="tuimianOption" autoresize class="chart" />
      </el-card>
    </div>

    <!-- 第五行：K-Means 聚类分析（独占一行） -->
    <div class="chart-row">
      <el-card shadow="never" class="chart-card chart-card-full">
        <template #header>
          <div class="algo-header">
            <h4>院校竞争力聚类分析（K-Means 算法）</h4>
            <el-tag type="danger" size="small">数据分析算法</el-tag>
          </div>
          <p class="algo-desc">
            基于 K-Means 聚类算法，从招生专业数、招生人数、双一流、985、211、自划线、博士点七个维度对院校进行竞争力分级
          </p>
        </template>
        <div class="cluster-content">
          <v-chart :option="clusterOption" autoresize class="chart chart-tall" />
          <div v-if="clusterCenters.length > 0" class="cluster-table">
            <h5>聚类中心特征</h5>
            <el-table :data="clusterCenters" border size="small" style="width: 100%">
              <el-table-column prop="tier" label="竞争力等级" width="120" />
              <el-table-column prop="major_count_avg" label="平均专业数" width="100" />
              <el-table-column prop="enrollment_avg" label="平均招生数" width="100" />
              <el-table-column prop="syl_ratio" label="双一流比例" width="100" />
              <el-table-column prop="b985_ratio" label="985比例" width="90" />
              <el-table-column prop="b211_ratio" label="211比例" width="90" />
              <el-table-column prop="zhx_ratio" label="自划线比例" width="100" />
              <el-table-column prop="bs_ratio" label="博士点比例" width="100" />
            </el-table>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 数据看板页面
 * 包含 9 个统计图表，支持全屏/退出全屏切换。
 */
import { ref, onMounted, onBeforeUnmount } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, PieChart, ScatterChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
} from 'echarts/components'
import {
  getOverviewApi,
  getProvinceUniversityCountApi,
  getEliteUniversityRatioApi,
  getDegreeTypeDistributionApi,
  getStudyModeDistributionApi,
  getZhxUniversityMajorCountApi,
  getCategoryDirectionCountApi,
  getProvinceEnrollmentApi,
  getUniversityTuimianRatioApi,
  getUniversityClusterAnalysisApi,
} from '@/api/dashboard'

use([
  CanvasRenderer, BarChart, PieChart, ScatterChart,
  TitleComponent, TooltipComponent, LegendComponent, GridComponent, DataZoomComponent,
])

const loading = ref(true)
const dashboardRef = ref<HTMLElement>()
const isFullscreen = ref(false)

// ===== 全屏切换 =====
function toggleFullscreen() {
  if (!isFullscreen.value) {
    dashboardRef.value?.requestFullscreen?.()
  } else {
    document.exitFullscreen?.()
  }
}

function onFullscreenChange() {
  isFullscreen.value = !!document.fullscreenElement
}

onMounted(() => {
  document.addEventListener('fullscreenchange', onFullscreenChange)
})

onBeforeUnmount(() => {
  document.removeEventListener('fullscreenchange', onFullscreenChange)
})

// ===== 概览数据 =====
const overviewCards = ref([
  { label: '数据总量', value: 0, color: '#e6a23c' },
  { label: '院校总数', value: 0, color: '#409eff' },
  { label: '专业总数', value: 0, color: '#67c23a' },
  { label: '门类数量', value: 0, color: '#909399' },
  { label: '覆盖省市', value: 0, color: '#f56c6c' },
  { label: '双一流院校', value: 0, color: '#e6a23c' },
])

// ===== 各图表配置 =====
const provinceUniOption = ref({})
const eliteRatioOption = ref({})
const degreeTypeOption = ref({})
const categoryDirOption = ref({})
const studyModeOption = ref({})
const zhxMajorOption = ref({})
const provinceEnrollOption = ref({})
const tuimianOption = ref({})
const clusterOption = ref({})
const clusterCenters = ref<any[]>([])

/** 生成柱状图配置 */
function barOption(categories: string[], values: number[], color = '#5470c6', hasZoom = false) {
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: hasZoom ? '15%' : '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: { rotate: 30, fontSize: 11 },
    },
    yAxis: { type: 'value' },
    dataZoom: hasZoom ? [{ type: 'slider', bottom: 0 }] : [],
    series: [{
      type: 'bar',
      data: values,
      itemStyle: { color },
      barMaxWidth: 40,
    }],
  }
}

/** 生成饼图配置 */
function pieOption(items: { name: string; value: number }[]) {
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, type: 'scroll' },
    series: [{
      type: 'pie',
      radius: ['35%', '65%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6 },
      label: { show: true, formatter: '{b}\n{c} ({d}%)' },
      data: items,
    }],
  }
}

onMounted(async () => {
  try {
    const [
      overviewRes, provUniRes, eliteRes, degreeRes, studyRes,
      zhxRes, catDirRes, provEnrollRes, tuimianRes, clusterRes,
    ] = await Promise.all([
      getOverviewApi(), getProvinceUniversityCountApi(), getEliteUniversityRatioApi(),
      getDegreeTypeDistributionApi(), getStudyModeDistributionApi(),
      getZhxUniversityMajorCountApi(), getCategoryDirectionCountApi(),
      getProvinceEnrollmentApi(), getUniversityTuimianRatioApi(),
      getUniversityClusterAnalysisApi(),
    ])

    // 概览数据
    const ov = overviewRes.data
    overviewCards.value = [
      { label: '数据总量', value: ov.total_records, color: '#e6a23c' },
      { label: '院校总数', value: ov.total_universities, color: '#409eff' },
      { label: '专业总数', value: ov.total_majors, color: '#67c23a' },
      { label: '门类数量', value: ov.total_categories, color: '#909399' },
      { label: '覆盖省市', value: ov.total_provinces, color: '#f56c6c' },
      { label: '双一流院校', value: ov.syl_count, color: '#e6a23c' },
    ]

    // 图表1：省市院校分布
    const provUni = provUniRes.data
    provinceUniOption.value = barOption(provUni.categories, provUni.values, '#5470c6', provUni.categories.length > 15)

    // 图表2：重点院校数量对比
    const elite = eliteRes.data
    eliteRatioOption.value = barOption(elite.categories, elite.values, '#ee6666', false)

    // 图表3：学位类型
    degreeTypeOption.value = pieOption(degreeRes.data.items)

    // 图表4：学习方式
    studyModeOption.value = pieOption(studyRes.data.items)

    // 图表5：门类招生方向数量
    const catDir = catDirRes.data
    categoryDirOption.value = barOption(catDir.categories, catDir.values, '#91cc75', catDir.categories.length > 10)

    // 图表6：自划线院校专业数 TOP15（横向条形图）
    const zhx = zhxRes.data
    zhxMajorOption.value = {
      tooltip: { trigger: 'axis' },
      grid: { left: '30%', right: '4%', bottom: '3%', containLabel: false },
      xAxis: { type: 'value' },
      yAxis: {
        type: 'category',
        data: [...zhx.categories].reverse(),
        axisLabel: { fontSize: 11 },
      },
      series: [{
        type: 'bar',
        data: [...zhx.values].reverse(),
        itemStyle: {
          color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [{ offset: 0, color: '#73c0de' }, { offset: 1, color: '#5470c6' }],
          },
        },
        barMaxWidth: 20,
      }],
    }

    // 图表7：省市招生人数
    const provEnroll = provEnrollRes.data
    provinceEnrollOption.value = barOption(provEnroll.categories, provEnroll.values, '#fac858', provEnroll.categories.length > 15)

    // 图表8：推免占比 TOP15
    const tm = tuimianRes.data
    tuimianOption.value = {
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          let s = params[0].name + '<br/>'
          for (const p of params) s += `${p.marker} ${p.seriesName}: ${p.value}<br/>`
          const idx = params[0].dataIndex
          s += `推免占比: ${tm.ratio_values[idx]}%`
          return s
        },
      },
      legend: { bottom: 0 },
      grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
      xAxis: { type: 'category', data: tm.categories, axisLabel: { rotate: 40, fontSize: 10 } },
      yAxis: { type: 'value', name: '人数' },
      series: [
        { name: '拟招生人数', type: 'bar', data: tm.total_values, itemStyle: { color: '#5470c6' } },
        { name: '推免人数', type: 'bar', data: tm.tuimian_values, itemStyle: { color: '#ee6666' } },
      ],
    }

    // 图表9：K-Means 聚类散点图
    const cluster = clusterRes.data
    clusterCenters.value = cluster.centers || []
    buildClusterChart(cluster)
  } finally {
    loading.value = false
  }
})

function buildClusterChart(data: any) {
  const tierColors: Record<string, string> = {
    '高竞争力': '#ee6666', '中等竞争力': '#fac858', '一般竞争力': '#91cc75',
  }
  const labels = data.labels || ['高竞争力', '中等竞争力', '一般竞争力']
  const seriesMap: Record<string, any[]> = {}
  labels.forEach((l: string) => { seriesMap[l] = [] })

  for (const item of (data.clusters || [])) {
    if (seriesMap[item.tier]) {
      const attrScore = item.is_syl + item.is_985 + item.is_211 + item.is_zhx + item.is_bs
      seriesMap[item.tier].push({
        value: [item.major_count, item.enrollment, attrScore * 4 + 8],
        name: item.dwmc, itemData: item,
      })
    }
  }

  clusterOption.value = {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const d = params.data.itemData
        if (!d) return params.name
        return `<strong>${d.dwmc}</strong><br/>` +
          `招生专业数: ${d.major_count}<br/>` +
          `拟招生人数: ${d.enrollment}<br/>` +
          `双一流: ${d.is_syl ? '是' : '否'} | 985: ${d.is_985 ? '是' : '否'} | 211: ${d.is_211 ? '是' : '否'}<br/>` +
          `自划线: ${d.is_zhx ? '是' : '否'} | 博士点: ${d.is_bs ? '是' : '否'}<br/>` +
          `竞争力等级: <strong>${d.tier}</strong>`
      },
    },
    legend: { data: labels, bottom: 0 },
    grid: { left: '3%', right: '10%', bottom: '12%', containLabel: true },
    xAxis: { type: 'value', name: '招生专业数量', nameLocation: 'middle', nameGap: 30 },
    yAxis: { type: 'value', name: '拟招生总人数', nameLocation: 'middle', nameGap: 50 },
    series: labels.map((label: string) => ({
      name: label, type: 'scatter',
      data: seriesMap[label] || [],
      symbolSize: (val: number[]) => val[2] || 10,
      itemStyle: { color: tierColors[label] || '#999' },
    })),
  }
}
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dashboard-page.is-fullscreen {
  background: #f5f5f5;
  padding: 16px;
  overflow-y: auto;
}

.dashboard-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.overview-row {
  display: flex;
  gap: 16px;
}

.overview-card {
  flex: 1;
  text-align: center;
}

.overview-value {
  font-size: 28px;
  font-weight: bold;
}

.overview-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.chart-row {
  display: flex;
  gap: 16px;
}

.chart-card {
  flex: 1;
  overflow: hidden;
}

.chart-card-full {
  flex: 1;
}

.chart {
  height: 360px;
  width: 100%;
}

.chart-tall {
  height: 420px;
}

.algo-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.algo-desc {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.cluster-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cluster-table h5 {
  font-size: 14px;
  margin-bottom: 8px;
  color: #303133;
}
</style>
