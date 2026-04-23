# 基于Python的考研院校数据检索与智能推荐系统

## 项目简介

本系统是一个面向考研学生的院校数据检索与智能推荐平台，提供多维度专业院校检索、基于内容的智能推荐算法、院校横向对比等核心功能，帮助考生科学选择目标院校。

## 技术栈

### 后端
- **Python 3.10+**
- **FastAPI** — 高性能 Web 框架
- **SQLAlchemy 2.0** — ORM 数据库操作
- **MySQL 8.0** — 关系型数据库
- **JWT (python-jose)** — 用户认证
- **Pandas / NumPy** — 推荐算法数据处理

### 前端
- **Vue 3** — Composition API + `<script setup>` 语法
- **TypeScript** — 类型安全
- **Vite** — 构建工具
- **Element Plus** — UI 组件库
- **Pinia** — 状态管理
- **Vue Router 4** — 路由管理
- **Axios** — HTTP 请求

## 项目结构

```
python-project/
├── backend/                    # 后端项目
│   ├── app/
│   │   ├── api/                # API 路由模块
│   │   │   ├── auth.py         # 用户认证接口
│   │   │   ├── search.py       # 多维检索接口
│   │   │   ├── recommend.py    # 智能推荐接口
│   │   │   └── workbench.py    # 工作台接口（收藏/对比）
│   │   ├── core/               # 核心配置
│   │   │   ├── config.py       # 全局配置
│   │   │   ├── database.py     # 数据库连接
│   │   │   └── security.py     # JWT 认证
│   │   ├── models/             # SQLAlchemy 数据模型
│   │   │   ├── major.py        # 专业信息表
│   │   │   ├── major_university.py  # 专业-院校关联表
│   │   │   ├── major_detail.py # 专业研究方向详情表
│   │   │   ├── user.py         # 用户表
│   │   │   ├── favorite.py     # 收藏表
│   │   │   └── recommend_log.py # 推荐记录表
│   │   ├── schemas/            # Pydantic 数据验证模型
│   │   ├── services/           # 业务逻辑服务
│   │   │   └── recommendation.py  # 核心推荐算法
│   │   └── main.py             # FastAPI 应用入口
│   └── requirements.txt        # Python 依赖
├── frontend/                   # 前端项目
│   ├── src/
│   │   ├── api/                # API 请求封装
│   │   ├── components/         # 公共组件
│   │   ├── router/             # 路由配置
│   │   ├── stores/             # Pinia 状态管理
│   │   ├── types/              # TypeScript 类型定义
│   │   ├── utils/              # 工具函数
│   │   └── views/              # 页面视图
│   └── package.json
├── sql/
│   └── init.sql                # 数据库初始化脚本
├── docker-compose.yml          # Docker Compose（MySQL）
└── README.md
```

## 功能模块

### 模块一：用户认证与画像管理
- JWT Token 认证（注册/登录）
- 考研意向画像问卷（意向门类、省市、学位类型、学习方式、实力自评）

### 模块二：多维检索引擎
- 三级级联选择器：门类 → 一级学科 → 专业
- 高级过滤面板：省市、双一流、自划线、博士点
- 分页展示匹配院校列表

### 模块三：智能推荐算法（核心）
- 基于内容的推荐（Content-Based Recommendation）
- 多维打分机制：
  - 难度系数：自划线(+5分)、双一流(+3分)、博士点(+1分)
  - 匹配度：省市匹配(+10分)、学习方式匹配(+5分)
- 三梯度展示：冲刺院校 / 稳妥院校 / 保底院校

### 模块四：我的工作台
- 院校收藏夹（收藏/取消收藏）
- 院校PK横向对比（2-3所院校属性对比）

## 快速开始

### 1. 启动 MySQL

```bash
docker-compose up -d
```

### 2. 启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（可选，复制并修改 .env.example）
cp .env.example .env

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端 API 文档：http://localhost:8000/docs

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端页面：http://localhost:5173

## API 接口一览

| 模块 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 认证 | POST | /api/auth/register | 用户注册 |
| 认证 | POST | /api/auth/login | 用户登录 |
| 认证 | GET | /api/auth/me | 获取当前用户信息 |
| 认证 | PUT | /api/auth/profile | 更新画像 |
| 检索 | GET | /api/search/categories | 获取门类列表 |
| 检索 | GET | /api/search/disciplines | 获取一级学科列表 |
| 检索 | GET | /api/search/majors | 获取专业列表 |
| 检索 | GET | /api/search/provinces | 获取省市列表 |
| 检索 | GET | /api/search/universities | 高级检索院校 |
| 推荐 | POST | /api/recommend/ | 获取智能推荐 |
| 工作台 | GET | /api/workbench/favorites | 获取收藏列表 |
| 工作台 | POST | /api/workbench/favorites | 添加收藏 |
| 工作台 | DELETE | /api/workbench/favorites/:id | 取消收藏 |
| 工作台 | GET | /api/workbench/favorites/check | 检查是否已收藏 |
| 工作台 | POST | /api/workbench/compare | 院校横向对比 |
