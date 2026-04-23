<template>
  <!-- 院校深度画像详情页 -->
  <div class="detail-page" v-loading="loading">
    <!-- 院校基本信息卡片 -->
    <el-card shadow="never" v-if="info">
      <template #header>
        <div class="info-header">
          <h2>{{ info.dwmc }}</h2>
          <div class="info-tags">
            <el-tag v-if="isYes(info.syl)" type="danger">双一流</el-tag>
            <el-tag v-if="isYes(info.b985)" type="danger">985</el-tag>
            <el-tag v-if="isYes(info.b211)" type="warning">211</el-tag>
            <el-tag v-if="isYes(info.zhx)" type="warning">自划线</el-tag>
            <el-tag v-if="isYes(info.bs)" type="success">博士点</el-tag>
            <el-tag v-if="isYes(info.yjsy)" type="info">研究生院</el-tag>
            <el-tag type="info" effect="plain">{{ info.szss }}</el-tag>
          </div>
        </div>
      </template>

      <!-- 数字概览 -->
      <div class="stat-row">
        <div class="stat-item">
          <div class="stat-num">{{ info.total_directions }}</div>
          <div class="stat-label">招生方向</div>
        </div>
        <div class="stat-item">
          <div class="stat-num" style="color:#67c23a">{{ info.total_majors }}</div>
          <div class="stat-label">涉及专业</div>
        </div>
        <div class="stat-item">
          <div class="stat-num" style="color:#e6a23c">{{ info.total_departments }}</div>
          <div class="stat-label">招生院系</div>
        </div>
        <div class="stat-item">
          <div class="stat-num" style="color:#f56c6c">{{ info.total_enrollment }}</div>
          <div class="stat-label">拟招生人数</div>
        </div>
        <div class="stat-item">
          <div class="stat-num" style="color:#909399">{{ info.total_tuimian }}</div>
          <div class="stat-label">推免人数</div>
        </div>
      </div>
    </el-card>

    <!-- 图表区域 -->
    <div class="chart-row">
      <!-- 统考 vs 推免饼图 -->
      <el-card shadow="never" class="chart-card">
        <template #header><h4>统考与推免名额比例</h4></template>
        <v-chart :option="enrollPieOption" style="height: 300px" autoresize />
      </el-card>

      <!-- 学习方式分布饼图 -->
      <el-card shadow="never" class="chart-card">
        <template #header><h4>学习方式分布</h4></template>
        <v-chart :option="studyPieOption" style="height: 300px" autoresize />
      </el-card>
    </div>

    <!-- 院系招生分布 -->
    <el-card shadow="never">
      <template #header><h4>院系招生分布 TOP20</h4></template>
      <v-chart :option="deptBarOption" style="height: 400px" autoresize />
    </el-card>

    <!-- 研究方向词云 -->
    <el-card shadow="never">
      <template #header><h4>研究方向词云分析</h4></template>
      <div v-if="wordcloudData.length > 0" class="wordcloud-container">
        <div v-for="(w, i) in wordcloudData.slice(0, 60)" :key="i"
          class="word-tag"
          :style="{ fontSize: wordSize(w.value) + 'px', color: wordColor(i) }"
        >
          {{ w.name }}
        </div>
      </div>
      <el-empty v-else description="暂无词云数据" :image-size="60" />
    </el-card>

    <!-- 专业研究方向列表 -->
    <el-card shadow="never">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <h4>专业研究方向列表</h4>
          <el-input v-model="progKeyword" placeholder="搜索专业/方向/院系" clearable style="width:240px" @keyup.enter="fetchPrograms" />
        </div>
      </template>
      <el-table :data="programs" v-loading="progLoading" stripe border style="width:100%">
        <el-table-column prop="yxsmc" label="院系所" min-width="150" show-overflow-tooltip />
        <el-table-column prop="zymc" label="专业名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="yjfxmc" label="研究方向" min-width="150" show-overflow-tooltip />
        <el-table-column prop="zdjs" label="指导教师" width="120" show-overflow-tooltip />
        <el-table-column prop="nzsrs" label="招生数" width="70" align="center" />
        <el-table-column prop="ssjstmrs" label="推免数" width="70" align="center" />
        <el-table-column prop="xxfs" label="学习方式" width="80">
          <template #default="{ row }">
            {{ row.xxfs === '1' ? '全日制' : row.xxfs === '2' ? '非全日制' : row.xxfs || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="考试科目" min-width="200">
          <template #default="{ row }">
            <div class="exam-subjects">
              <span v-if="row.km1mc">①{{ row.km1mc }}</span>
              <span v-if="row.km2mc">②{{ row.km2mc }}</span>
              <span v-if="row.km3mc">③{{ row.km3mc }}</span>
              <span v-if="row.km4mc">④{{ row.km4mc }}</span>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination
          v-model:current-page="progPage"
          :page-size="15"
          :total="progTotal"
          layout="total, prev, pager, next"
          @current-change="fetchPrograms"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
/**
 * 院校深度画像页面
 * 展示单所院校的全方位数据：基本信息、统考/推免比例、院系分布、研究方向词云、专业列表。
 */
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import VChart from 'vue-echarts'
import {
  getUniversityDetailApi,
  getEnrollmentPieApi,
  getDepartmentBarApi,
  getStudyModePieApi,
  getUniversityProgramsApi,
} from '@/api/university'
import { getWordcloudApi } from '@/api/analysis'

const route = useRoute()
const dwdm = route.query.dwdm as string

const loading = ref(true)
const info = ref<any>(null)
const enrollPieOption = ref({})
const studyPieOption = ref({})
const deptBarOption = ref({})
const wordcloudData = ref<{ name: string; value: number }[]>([])
const programs = ref<any[]>([])
const progLoading = ref(false)
const progPage = ref(1)
const progTotal = ref(0)
const progKeyword = ref('')

function isYes(val?: string): boolean {
  return val === '是' || val === '1'
}

/** 词云字号映射 */
function wordSize(value: number): number {
  const max = wordcloudData.value[0]?.value || 1
  return Math.max(14, Math.min(36, Math.round((value / max) * 36)))
}

/** 词云颜色 */
const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#5470c6', '#91cc75', '#ee6666', '#73c0de', '#fc8452']
function wordColor(index: number): string {
  return colors[index % colors.length]
}

/** 饼图通用配置 */
function pieOption(items: { name: string; value: number }[]) {
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie', radius: ['40%', '70%'],
      label: { formatter: '{b}\n{d}%' },
      data: items,
    }],
  }
}

onMounted(async () => {
  if (!dwdm) { loading.value = false; return }

  try {
    const [detailRes, enrollRes, studyRes, deptRes, wcRes] = await Promise.all([
      getUniversityDetailApi(dwdm),
      getEnrollmentPieApi(dwdm),
      getStudyModePieApi(dwdm),
      getDepartmentBarApi(dwdm),
      getWordcloudApi({ dwdm }),
    ])

    info.value = detailRes.data
    enrollPieOption.value = pieOption(enrollRes.data.items)
    studyPieOption.value = pieOption(studyRes.data.items)

    // 院系分布横向条形图
    const dept = deptRes.data
    const cats = [...dept.categories].reverse()
    const vals = [...dept.direction_counts].reverse()
    deptBarOption.value = {
      tooltip: { trigger: 'axis' },
      grid: { left: '30%', right: '6%', bottom: '3%', containLabel: false },
      yAxis: { type: 'category', data: cats, axisLabel: { fontSize: 11 } },
      xAxis: { type: 'value', name: '招生方向数' },
      series: [{
        type: 'bar', data: vals,
        itemStyle: {
          color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [{ offset: 0, color: '#409eff' }, { offset: 1, color: '#67c23a' }],
          },
        },
      }],
    }

    wordcloudData.value = wcRes.data.words || []
  } finally {
    loading.value = false
  }

  fetchPrograms()
})

async function fetchPrograms() {
  progLoading.value = true
  try {
    const res = await getUniversityProgramsApi({
      dwdm,
      keyword: progKeyword.value || undefined,
      page: progPage.value,
      page_size: 15,
    })
    programs.value = res.data.items
    progTotal.value = res.data.total
  } finally {
    progLoading.value = false
  }
}
</script>

<style scoped>
.detail-page { display: flex; flex-direction: column; gap: 16px; }
.info-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.info-header h2 { margin: 0; }
.info-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.stat-row { display: flex; gap: 20px; flex-wrap: wrap; }
.stat-item { flex: 1; min-width: 100px; text-align: center; padding: 12px 0; }
.stat-num { font-size: 26px; font-weight: bold; color: #409eff; }
.stat-label { font-size: 13px; color: #909399; margin-top: 4px; }
.chart-row { display: flex; gap: 16px; }
.chart-card { flex: 1; }
.wordcloud-container {
  display: flex; flex-wrap: wrap; gap: 10px; padding: 16px;
  justify-content: center; align-items: center; min-height: 200px;
}
.word-tag { font-weight: 500; cursor: default; transition: transform 0.2s; }
.word-tag:hover { transform: scale(1.2); }
.exam-subjects { display: flex; flex-direction: column; gap: 2px; font-size: 12px; color: #606266; }
.pagination { margin-top: 16px; display: flex; justify-content: center; }
</style>
