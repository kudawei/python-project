/**
 * 全局类型定义
 * 定义前后端交互的数据结构接口
 */

/** 级联选择器选项 */
export interface CascadeOption {
  value: string
  label: string
}

/** 登录/注册响应 Token */
export interface TokenResponse {
  access_token: string
  token_type: string
  user_id: number
  username: string
  profile_completed: number
}

/** 用户信息 */
export interface UserInfo {
  id: number
  username: string
  nickname?: string
  email?: string
  target_mldm?: string
  target_mlmc?: string
  target_provinces?: string[]
  degree_type?: string
  study_mode?: string
  self_rating?: string
  profile_completed: number
}

/** 用户画像表单 */
export interface UserProfile {
  target_mldm?: string
  target_mlmc?: string
  target_provinces?: string[]
  degree_type?: string
  study_mode?: string
  self_rating?: string
}

/** 院校列表项 */
export interface UniversityItem {
  id: number
  dwdm?: string
  dwmc?: string
  szss?: string
  zhx?: string
  bs?: string
  syl?: string
  xxfs?: string
  tydxs?: string
  jsggjh?: string
  zydm?: string
  zymc?: string
}

/** 检索结果分页响应 */
export interface SearchResponse {
  total: number
  page: number
  page_size: number
  items: UniversityItem[]
}

/** 推荐结果项 */
export interface RecommendItem {
  dwdm?: string
  dwmc?: string
  szss?: string
  zhx?: string
  bs?: string
  syl?: string
  xxfs?: string
  score: number
  tier: string
  tier_label: string
}

/** 推荐响应 */
export interface RecommendResponse {
  sprint: RecommendItem[]
  stable: RecommendItem[]
  safe: RecommendItem[]
}

/** 收藏项 */
export interface FavoriteItem {
  id: number
  dwdm: string
  dwmc?: string
  zydm: string
  zymc?: string
  created_at?: string
}

/** 对比项 */
export interface CompareItem {
  dwdm?: string
  dwmc?: string
  szss?: string
  zhx?: string
  bs?: string
  syl?: string
  xxfs?: string
  tydxs?: string
  jsggjh?: string
  zydm?: string
  zymc?: string
  b985?: string
  b211?: string
  yjsy?: string
  yxsmc?: string
  yjfxmc?: string
  zdjs?: string
  nzsrs?: number
  km1mc?: string
  km2mc?: string
  km3mc?: string
  km4mc?: string
}
