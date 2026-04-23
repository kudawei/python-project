<template>
  <!-- 数据看板页面 —— 包含 9 个统计图表 -->
  <div class="dashboard-page" v-loading="loading">

    <!-- 顶部概览卡片 -->
    <div class="overview-row">
      <el-card v-for="card in overviewCards" :key="card.label" shadow="hover" class="overview-card">
        <div class="overview-value">{{ card.value }}</div>
        <div class="overview-label">{{ card.label }}</div>
      </el-card>
    </div>

    <!-- 第一行图表：门类院校分布 + 双一流占比 + 学位类型分布 -->
    <div class="chart-row">
      <el-card shadow="never" class="chart-card chart-card-lg">
        <template #header><h4>各门类院校数量分布</h4></template>
        <v-chart :option="categoryUniOption" autoresize class="chart" />
      </el-card>
      <el-card shadow="never" class="chart-card chart-card-sm">
        <template #header><h4>双一流院校占比</h4></template>
        <v-chart :option="sylRatioOption" autoresize class="chart" />
      </el-card>
      <el-card shadow="never" class="chart-card chart-card-sm">
        <template #header><h4>学位类型分布</h4></template>
        <v-chart :option="degreeTypeOption" autoresize class="chart" />
      </el-card>
    </div>

    <!-- 第二行图表：省市院校分布 + 学习方式分布 + 自划线对比 -->
    <div class="chart-row">
      <el-card shadow="never" class="chart-card chart-card-lg">
        <template #header><h4>各省市院校数量分布</h4></template>
        <v-chart :option="provinceUniOption" autoresize class="chart" />
      </el-card>
      <el-card shadow="never" class="chart-card chart-card-sm">
        <template #header><h4>学习方式分布</h4></template>
        <v-chart :option="studyModeOption" autoresize class="chart" />
      </el-card>
      <el-card shadow="never" class="chart-card chart-card-sm">
        <template #header><h4>自划线 vs 非自划线院校</h4></template>
        <v-chart :option="zhxCompareOption" autoresize class="chart" />
      </el-card>
    </div>

    <!-- 第三行图表：门类专业TOP10 + 博士点省市分布 -->
    <div class="chart-row">
      <el-card shadow="never" class="chart-card chart-card-md">
        <template #header><h4>各门类专业数量 TOP10</h4></template>
        <v-chart :option="majorTop10Option" autoresize class="chart" />
      </el-card>
      <el-card shadow="never" class="chart-card chart-card-md">
        <template #header><h4>博士点院校省市分布</h4></template>
        <v-chart :option="bsProvinceOption" autoresize class="chart" />
      </el-card>
    </div>

    <!-- 第四行图表：K-Means 聚类分析（数据分析算法） -->
    <div class="chart-row">
      <el-card shadow="never" class="chart-card chart-card-full">
        <template #header>
          <div class="algo-header">
            <h4>院校竞争力聚类分析（K-Means 算法）</h4>
            <el-tag type="danger" size="small">数据分析算法</el-tag>
          </div>
          <p class="algo-desc">
            基于 K-Means 聚类算法，从招生专业数、双一流、自划线、博士点四个维度对院校进行竞争力分级
          </p>
        </template>
        <div class="cluster-content">
          <v-chart :option="clusterOption" autoresize class="chart chart-tall" />
          <!-- 聚类中心统计表 -->
          <div v-if="clusterCenters.length > 0" class="cluster-table">
            <h5>聚类中心特征</h5>
            <el-table :data="clusterCenters" border size="small" style="width: 100%">
              <el-table-column prop="tier" label="竞争力等级" width="120" />
              <el-table-column prop="major_count_avg" label="平均专业数" width="110" />
              <el-table-column prop="syl_ratio" label="双一流比例" width="110" />
              <el-table-column prop="zhx_ratio" label="自划线比例" width="110" />
              <el-table-column prop="bs_ratio" label="博士点比例" width="110" />
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
 * 包含 9 个统计图表：
 * 1. 各门类院校数量分布（柱状图）
 * 2. 双一流院校占比（饼图）
 * 3. 学位类型分布（饼图）
 * 4. 各省市院校数量分布（柱状图）
 * 5. 学习方式分布（饼图）
 * 6. 自划线 vs 非自划线院校对比（分组柱状图）
 * 7. 各门类专业数量 TOP10（横向条形图）
 * 8. 博士点院校省市分布（柱状图）
 * 9. 院校竞争力聚类分析 —— K-Means 算法（散点图）
 */
import { ref, onMounted } from 'vue'
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
  getCategoryUniversityCountApi,
  getProvinceUniversityCountApi,
  getSylRatioApi,
  getDegreeTypeDistributionApi,
  getStudyModeDistributionApi,
  getZhxComparisonApi,
  getCategoryMajorTop10Api,
  getBsProvinceDistributionApi,
  getUniversityClusterAnalysisApi,
} from '@/api/dashboard'

// 注册 ECharts 组件（按需引入，减小打包体积）
use([
  CanvasRenderer,
  BarChart,
  PieChart,
  ScatterChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
])

const loading = ref(true)

// ===== 概览数据 =====
const overviewCards = ref([
  { label: '院校总数', value: 0 },
  { label: '专业总数', value: 0 },
  { label: '门类数量', value: 0 },
  { label: '覆盖省市', value: 0 },
  { label: '双一流院校', value: 0 },
])

// ===== 图表1：各门类院校数量分布 =====
const categoryUniOption = ref({})
// ===== 图表2：双一流占比 =====
const sylRatioOption = ref({})
// ===== 图表3：学位类型分布 =====
const degreeTypeOption = ref({})
// ===== 图表4：省市院校分布 =====
const provinceUniOption = ref({})
// ===== 图表5：学习方式分布 =====
const studyModeOption = ref({})
// ===== 图表6：自划线对比 =====
const zhxCompareOption = ref({})
// ===== 图表7：门类专业 TOP10 =====
const majorTop10Option = ref({})
// ===== 图表8：博士点省市分布 =====
const bsProvinceOption = ref({})
// ===== 图表9：聚类分析 =====
const clusterOption = ref({})
const clusterCenters = ref<any[]>([])

/** ECharts 配色方案 */
const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc']

/** 生成柱状图配置 */
function barOption(categories: string[], values: number[], color = '#5470c6') {
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: { rotate: 30, fontSize: 11 },
    },
    yAxis: { type: 'value' },
    dataZoom: categories.length > 15 ? [{ type: 'slider', bottom: 0 }] : [],
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
      label: { show: true, formatter: '{b}\n{d}%' },
      data: items,
    }],
  }
}

onMounted(async () => {
  try {
    // 并行请求所有数据
    const [
      overviewRes,
      catUniRes,
      provUniRes,
      sylRes,
      degreeRes,
      studyRes,
      zhxRes,
      top10Res,
      bsProvRes,
      clusterRes,
    ] = await Promise.all([
      getOverviewApi(),
      getCategoryUniversityCountApi(),
      getProvinceUniversityCountApi(),
      getSylRatioApi(),
      getDegreeTypeDistributionApi(),
      getStudyModeDistributionApi(),
      getZhxComparisonApi(),
      getCategoryMajorTop10Api(),
      getBsProvinceDistributionApi(),
      getUniversityClusterAnalysisApi(),
    ])

    // 概览数据
    const ov = overviewRes.data
    overviewCards.value = [
      { label: '院校总数', value: ov.total_universities },
      { label: '专业总数', value: ov.total_majors },
      { label: '门类数量', value: ov.total_categories },
      { label: '覆盖省市', value: ov.total_provinces },
      { label: '双一流院校', value: ov.syl_count },
    ]

    // 图表1：门类院校分布
    const catUni = catUniRes.data
    categoryUniOption.value = barOption(catUni.categories, catUni.values, '#5470c6')

    // 图表2：双一流占比
    sylRatioOption.value = pieOption(sylRes.data.items)

    // 图表3：学位类型
    degreeTypeOption.value = pieOption(degreeRes.data.items)

    // 图表4：省市院校分布
    const provUni = provUniRes.data
    provinceUniOption.value = barOption(provUni.categories, provUni.values, '#91cc75')

    // 图表5：学习方式
    studyModeOption.value = pieOption(studyRes.data.items)

    // 图表6：自划线对比（分组柱状图）
    const zhx = zhxRes.data
    zhxCompareOption.value = {
      tooltip: { trigger: 'axis' },
      legend: { bottom: 0 },
      grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
      xAxis: { type: 'category', data: zhx.categories },
      yAxis: { type: 'value' },
      series: zhx.series.map((s: any, i: number) => ({
        name: s.name,
        type: 'bar',
        data: s.values,
        itemStyle: { color: colors[i] },
      })),
    }

    // 图表7：门类专业 TOP10（横向条形图）
    const t10 = top10Res.data
    majorTop10Option.value = {
      tooltip: { trigger: 'axis' },
      grid: { left: '25%', right: '4%', bottom: '3%', containLabel: false },
      xAxis: { type: 'value' },
      yAxis: {
        type: 'category',
        data: [...t10.categories].reverse(),
        axisLabel: { fontSize: 12 },
      },
      series: [{
        type: 'bar',
        data: [...t10.values].reverse(),
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [
              { offset: 0, color: '#73c0de' },
              { offset: 1, color: '#5470c6' },
            ],
          },
        },
        barMaxWidth: 24,
      }],
    }

    // 图表8：博士点省市分布
    const bsProv = bsProvRes.data
    bsProvinceOption.value = barOption(bsProv.categories, bsProv.values, '#ee6666')

    // 图表9：K-Means 聚类散点图
    const cluster = clusterRes.data
    clusterCenters.value = cluster.centers || []
    buildClusterChart(cluster)
  } finally {
    loading.value = false
  }
})

/** 构建 K-Means 聚类散点图配置 */
function buildClusterChart(data: any) {
  const tierColors: Record<string, string> = {
    '高竞争力': '#ee6666',
    '中等竞争力': '#fac858',
    '一般竞争力': '#91cc75',
  }
  const labels = data.labels || ['高竞争力', '中等竞争力', '一般竞争力']

  // 按聚类分组
  const seriesMap: Record<string, any[]> = {}
  labels.forEach((l: string) => { seriesMap[l] = [] })

  for (const item of (data.clusters || [])) {
    const tier = item.tier
    if (seriesMap[tier]) {
      seriesMap[tier].push({
        value: [item.major_count, item.is_syl + item.is_zhx + item.is_bs],
        name: item.dwmc,
        itemData: item,
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
          `双一流: ${d.is_syl ? '是' : '否'}<br/>` +
          `自划线: ${d.is_zhx ? '是' : '否'}<br/>` +
          `博士点: ${d.is_bs ? '是' : '否'}<br/>` +
          `竞争力等级: ${d.tier}`
      },
    },
    legend: { data: labels, bottom: 0 },
    grid: { left: '3%', right: '10%', bottom: '12%', containLabel: true },
    xAxis: {
      type: 'value',
      name: '招生专业数量',
      nameLocation: 'middle',
      nameGap: 30,
    },
    yAxis: {
      type: 'value',
      name: '院校属性得分\n(双一流+自划线+博士点)',
      nameLocation: 'middle',
      nameGap: 40,
      max: 3,
    },
    series: labels.map((label: string) => ({
      name: label,
      type: 'scatter',
      data: seriesMap[label] || [],
      symbolSize: 12,
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

/* 顶部概览卡片 */
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
  color: #409eff;
}

.overview-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

/* 图表行 */
.chart-row {
  display: flex;
  gap: 16px;
}

.chart-card {
  overflow: hidden;
}

.chart-card-lg {
  flex: 2;
}

.chart-card-sm {
  flex: 1;
}

.chart-card-md {
  flex: 1;
}

.chart-card-full {
  flex: 1;
}

.chart {
  height: 320px;
  width: 100%;
}

.chart-tall {
  height: 400px;
}

/* 聚类分析区域 */
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
