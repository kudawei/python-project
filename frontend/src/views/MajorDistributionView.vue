<template>
  <!-- 专业院校省市分布分析页面 -->
  <div class="dist-page">
    <el-card shadow="never">
      <template #header>
        <h3>专业院校省市分布</h3>
        <p class="sub-title">选择一个专业，查看全国各省市开设该专业的院校数量分布</p>
      </template>

      <!-- 级联选择器 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="门类">
          <el-select v-model="selectedMldm" placeholder="请选择门类" clearable @change="onCategoryChange" style="width:160px">
            <el-option v-for="c in categories" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="一级学科">
          <el-select v-model="selectedYjxkdm" placeholder="请先选门类" clearable @change="onDisciplineChange" style="width:200px">
            <el-option v-for="d in disciplines" :key="d.value" :label="d.label" :value="d.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="专业">
          <el-select v-model="selectedZydm" placeholder="请先选学科" clearable style="width:220px">
            <el-option v-for="m in majors" :key="m.value" :label="m.label" :value="m.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :disabled="!selectedZydm" @click="fetchDistribution">查看分布</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 分布图 -->
    <el-card v-if="distData" shadow="never">
      <template #header>
        <h4>{{ distData.zymc }} — 全国院校分布（共 {{ distData.total_universities }} 所，覆盖 {{ distData.total_provinces }} 个省市）</h4>
      </template>
      <v-chart :option="barOption" style="height: 450px" autoresize />
    </el-card>

    <!-- 词云分析 -->
    <el-card v-if="wordcloudWords.length > 0" shadow="never">
      <template #header>
        <h4>{{ distData?.zymc || '' }} — 研究方向词云</h4>
      </template>
      <div class="wordcloud-container">
        <div v-for="(w, i) in wordcloudWords.slice(0, 60)" :key="i"
          class="word-tag"
          :style="{ fontSize: wordSize(w.value) + 'px', color: wordColor(i) }"
        >
          {{ w.name }}
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
/**
 * 专业院校省市分布分析页面
 * 选择专业后展示该专业在全国各省市的院校数量分布柱状图，
 * 以及基于 NLP 分词的研究方向词云。
 */
import { ref, onMounted } from 'vue'
import VChart from 'vue-echarts'
import type { CascadeOption } from '@/types'
import { getCategoriesApi, getDisciplinesApi, getMajorsApi } from '@/api/search'
import { getMajorProvinceDistributionApi, getWordcloudApi } from '@/api/analysis'

const categories = ref<CascadeOption[]>([])
const disciplines = ref<CascadeOption[]>([])
const majors = ref<CascadeOption[]>([])
const selectedMldm = ref('')
const selectedYjxkdm = ref('')
const selectedZydm = ref('')
const distData = ref<any>(null)
const barOption = ref({})
const wordcloudWords = ref<{ name: string; value: number }[]>([])

const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#5470c6', '#91cc75', '#ee6666', '#73c0de', '#fc8452']
function wordColor(i: number) { return colors[i % colors.length] }
function wordSize(value: number) {
  const max = wordcloudWords.value[0]?.value || 1
  return Math.max(14, Math.min(36, Math.round((value / max) * 36)))
}

onMounted(async () => {
  const res = await getCategoriesApi()
  categories.value = res.data
})

async function onCategoryChange() {
  selectedYjxkdm.value = ''
  selectedZydm.value = ''
  disciplines.value = []
  majors.value = []
  if (selectedMldm.value) {
    const res = await getDisciplinesApi(selectedMldm.value)
    disciplines.value = res.data
  }
}

async function onDisciplineChange() {
  selectedZydm.value = ''
  majors.value = []
  if (selectedYjxkdm.value) {
    const res = await getMajorsApi(selectedYjxkdm.value)
    majors.value = res.data
  }
}

async function fetchDistribution() {
  if (!selectedZydm.value) return
  const [distRes, wcRes] = await Promise.all([
    getMajorProvinceDistributionApi(selectedZydm.value),
    getWordcloudApi({ zydm: selectedZydm.value }),
  ])

  distData.value = distRes.data
  wordcloudWords.value = wcRes.data.words || []

  barOption.value = {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
    xAxis: {
      type: 'category', data: distRes.data.categories,
      axisLabel: { rotate: 30, fontSize: 11 },
    },
    yAxis: { type: 'value', name: '院校数量' },
    series: [{
      type: 'bar', data: distRes.data.values,
      itemStyle: {
        color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: '#409eff' }, { offset: 1, color: '#67c23a' }],
        },
      },
    }],
  }
}
</script>

<style scoped>
.dist-page { display: flex; flex-direction: column; gap: 16px; }
.sub-title { font-size: 13px; color: #909399; margin-top: 4px; }
.filter-form { margin-bottom: 8px; }
.wordcloud-container {
  display: flex; flex-wrap: wrap; gap: 10px; padding: 16px;
  justify-content: center; align-items: center; min-height: 200px;
}
.word-tag { font-weight: 500; cursor: default; transition: transform 0.2s; }
.word-tag:hover { transform: scale(1.2); }
</style>
