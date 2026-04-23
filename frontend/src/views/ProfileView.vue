<template>
  <!-- 用户考研意向画像页面 -->
  <div class="profile-page">
    <el-card shadow="never">
      <template #header>
        <h3>考研意向画像问卷</h3>
        <p class="sub-title">
          请填写您的考研意向信息，系统将据此为您提供个性化的院校推荐
        </p>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        label-position="right"
        size="large"
        style="max-width: 600px; margin: 0 auto"
      >
        <!-- 意向门类选择 -->
        <el-form-item label="意向门类" prop="target_mldm">
          <el-select
            v-model="form.target_mldm"
            placeholder="请选择意向门类"
            @change="onCategoryChange"
            style="width: 100%"
          >
            <el-option
              v-for="item in categories"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <!-- 意向省市（多选） -->
        <el-form-item label="意向省市" prop="target_provinces">
          <el-select
            v-model="form.target_provinces"
            multiple
            placeholder="请选择意向省市（可多选）"
            style="width: 100%"
          >
            <el-option
              v-for="item in provinces"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <!-- 学位期望 -->
        <el-form-item label="学位期望" prop="degree_type">
          <el-radio-group v-model="form.degree_type">
            <el-radio value="xs">学术学位</el-radio>
            <el-radio value="zy">专业学位</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 学习方式期望 -->
        <el-form-item label="学习方式" prop="study_mode">
          <el-radio-group v-model="form.study_mode">
            <el-radio value="1">全日制</el-radio>
            <el-radio value="2">非全日制</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 实力自评 -->
        <el-form-item label="实力自评" prop="self_rating">
          <el-radio-group v-model="form.self_rating">
            <el-radio value="weak">较弱（基础一般）</el-radio>
            <el-radio value="medium">中等（有一定基础）</el-radio>
            <el-radio value="strong">较强（基础扎实）</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 提交按钮 -->
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">
            保存画像
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
/**
 * 用户画像页面
 * 用户填写考研意向问卷，数据用于智能推荐算法。
 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { CascadeOption } from '@/types'
import { getCategoriesApi, getProvincesApi } from '@/api/search'
import { updateProfileApi } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

/** 门类选项列表 */
const categories = ref<CascadeOption[]>([])
/** 省市选项列表 */
const provinces = ref<CascadeOption[]>([])

const form = reactive({
  target_mldm: '',
  target_mlmc: '',
  target_provinces: [] as string[],
  degree_type: '',
  study_mode: '',
  self_rating: '',
})

const rules: FormRules = {
  target_mldm: [{ required: true, message: '请选择意向门类', trigger: 'change' }],
  target_provinces: [{ required: true, message: '请选择意向省市', trigger: 'change' }],
  degree_type: [{ required: true, message: '请选择学位期望', trigger: 'change' }],
  study_mode: [{ required: true, message: '请选择学习方式', trigger: 'change' }],
  self_rating: [{ required: true, message: '请选择实力自评', trigger: 'change' }],
}

/** 页面加载时获取门类和省市选项 */
onMounted(async () => {
  const [catRes, provRes] = await Promise.all([
    getCategoriesApi(),
    getProvincesApi(),
  ])
  categories.value = catRes.data
  provinces.value = provRes.data

  // 如果用户已有画像数据，回显到表单
  if (userStore.userInfo) {
    const u = userStore.userInfo
    form.target_mldm = u.target_mldm || ''
    form.target_mlmc = u.target_mlmc || ''
    form.target_provinces = u.target_provinces || []
    form.degree_type = u.degree_type || ''
    form.study_mode = u.study_mode || ''
    form.self_rating = u.self_rating || ''
  }
})

/** 门类选择变更时，同步门类名称 */
function onCategoryChange(val: string) {
  const found = categories.value.find((c) => c.value === val)
  form.target_mlmc = found?.label || ''
}

/** 提交画像 */
async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await updateProfileApi({
      target_mldm: form.target_mldm,
      target_mlmc: form.target_mlmc,
      target_provinces: form.target_provinces,
      degree_type: form.degree_type,
      study_mode: form.study_mode,
      self_rating: form.self_rating,
    })
    ElMessage.success('画像保存成功')
    await userStore.fetchUserInfo()
  } catch {
    // 错误已在拦截器中处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.profile-page {
  max-width: 800px;
  margin: 0 auto;
}

.sub-title {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}
</style>
