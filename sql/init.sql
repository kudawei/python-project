-- 考研院校数据检索与智能推荐系统 - 数据库初始化脚本
-- 创建核心业务表和辅助表

USE kaoyan_db;

-- 表1：研究生专业信息表 major
CREATE TABLE IF NOT EXISTS `major` (
  `id` int NOT NULL AUTO_INCREMENT,
  `zydm` varchar(20) NOT NULL COMMENT '专业代码',
  `zymc` varchar(100) NOT NULL COMMENT '专业名称',
  `mldm` varchar(10) DEFAULT NULL COMMENT '门类代码',
  `mlmc` varchar(50) DEFAULT NULL COMMENT '门类名称',
  `yjxkdm` varchar(20) DEFAULT NULL COMMENT '一级学科代码',
  `yjxkmc` varchar(100) DEFAULT NULL COMMENT '一级学科名称',
  `xwlx` varchar(10) DEFAULT NULL COMMENT '学位类型: xs=学术学位, zy=专业学位',
  `xwlxmc` varchar(20) DEFAULT NULL COMMENT '学位类型名称',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_zydm_xwlx` (`zydm`,`xwlx`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='研究生专业信息表';

-- 表2：专业-院校关联表 major_university
CREATE TABLE IF NOT EXISTS `major_university` (
  `id` int NOT NULL AUTO_INCREMENT,
  `zydm` varchar(20) NOT NULL COMMENT '专业代码',
  `zymc` varchar(100) NOT NULL COMMENT '专业名称',
  `mldm` varchar(10) DEFAULT NULL COMMENT '门类代码',
  `mlmc` varchar(50) DEFAULT NULL COMMENT '门类名称',
  `yjxkdm` varchar(20) DEFAULT NULL COMMENT '一级学科代码',
  `yjxkmc` varchar(100) DEFAULT NULL COMMENT '一级学科名称',
  `xwlx` varchar(10) DEFAULT NULL COMMENT '学位类型',
  `xwlxmc` varchar(20) DEFAULT NULL COMMENT '学位类型名称',
  `sch_id` varchar(20) DEFAULT NULL COMMENT '院校ID',
  `dwdm` varchar(20) DEFAULT NULL COMMENT '院校代码',
  `dwmc` varchar(200) DEFAULT NULL COMMENT '院校名称',
  `szssm` varchar(10) DEFAULT NULL COMMENT '省市代码',
  `szss` varchar(50) DEFAULT NULL COMMENT '省市名称',
  `zhx` varchar(5) DEFAULT NULL COMMENT '是否自划线院校(是/否)',
  `bs` varchar(5) DEFAULT NULL COMMENT '是否有博士点(是/否)',
  `syl` varchar(5) DEFAULT NULL COMMENT '是否双一流(是/否)',
  `xxfs` varchar(20) DEFAULT NULL COMMENT '学习方式(全日制/非全日制)',
  `tydxs` varchar(5) DEFAULT NULL COMMENT '是否接收退役大学生士兵计划',
  `jsggjh` varchar(5) DEFAULT NULL COMMENT '是否接收少数民族骨干计划',
  PRIMARY KEY (`id`),
  KEY `idx_zydm` (`zydm`),
  KEY `idx_dwdm` (`dwdm`),
  KEY `idx_dwmc` (`dwmc`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='专业-院校关联表';

-- 表3：专业研究方向详情表 major_detail
CREATE TABLE IF NOT EXISTS `major_detail` (
  `id` int NOT NULL AUTO_INCREMENT,
  `zyyjfxdm` varchar(50) DEFAULT NULL COMMENT '专业研究方向代码',
  `zydm` varchar(20) NOT NULL COMMENT '专业代码',
  `zymc` varchar(100) DEFAULT NULL COMMENT '专业名称',
  `mldm` varchar(10) DEFAULT NULL COMMENT '门类代码',
  `mlmc` varchar(50) DEFAULT NULL COMMENT '门类名称',
  `yjxkdm` varchar(20) DEFAULT NULL COMMENT '一级学科代码',
  `yjxkmc` varchar(100) DEFAULT NULL COMMENT '一级学科名称',
  `xwlx` varchar(10) DEFAULT NULL COMMENT '学位类型 xs/zy',
  `xwlxmc` varchar(20) DEFAULT NULL COMMENT '学位类型名称',
  `dwdm` varchar(20) NOT NULL COMMENT '院校代码',
  `dwmc` varchar(200) DEFAULT NULL COMMENT '院校名称',
  `sch_id` varchar(20) DEFAULT NULL COMMENT 'schId',
  `szssm` varchar(10) DEFAULT NULL COMMENT '省市码',
  `szss` varchar(50) DEFAULT NULL COMMENT '省市',
  `zhx` varchar(5) DEFAULT NULL COMMENT '自划线',
  `bs` varchar(5) DEFAULT NULL COMMENT '博士点',
  `syl` varchar(5) DEFAULT NULL COMMENT '双一流',
  `b985` varchar(5) DEFAULT NULL COMMENT '985',
  `b211` varchar(5) DEFAULT NULL COMMENT '211',
  `yjsy` varchar(5) DEFAULT NULL COMMENT '研究生院',
  `ksfsdm` varchar(10) DEFAULT NULL COMMENT '考试方式代码',
  `ksfsmc` varchar(50) DEFAULT NULL COMMENT '考试方式名称',
  `yxsdm` varchar(20) DEFAULT NULL COMMENT '院系所代码',
  `yxsmc` varchar(200) DEFAULT NULL COMMENT '院系所名称',
  `yjfxdm` varchar(20) DEFAULT NULL COMMENT '研究方向代码',
  `yjfxmc` varchar(200) DEFAULT NULL COMMENT '研究方向名称',
  `zdjs` varchar(500) DEFAULT NULL COMMENT '指导教师',
  `nzsrs` int DEFAULT NULL COMMENT '拟招生人数',
  `nzsrsstr` varchar(200) DEFAULT NULL COMMENT '拟招生人数说明',
  `xxfs` varchar(10) DEFAULT NULL COMMENT '学习方式 1全日制 2非全日制',
  `gbfs` varchar(10) DEFAULT NULL COMMENT '公布方式',
  `tydxs` varchar(10) DEFAULT NULL COMMENT '退役大学生士兵计划',
  `jsggjh` varchar(10) DEFAULT NULL COMMENT '少骨计划',
  `ssjstmrs` int DEFAULT NULL COMMENT '招收推免人数',
  `ssncszjh` int DEFAULT NULL COMMENT '少骨计划人数',
  `cxzrs` int DEFAULT NULL COMMENT '从校招生人数',
  `zybz` text COMMENT '专业备注',
  `km1dm` varchar(20) DEFAULT NULL COMMENT '科目1代码',
  `km1mc` varchar(100) DEFAULT NULL COMMENT '科目1名称',
  `km2dm` varchar(20) DEFAULT NULL COMMENT '科目2代码',
  `km2mc` varchar(100) DEFAULT NULL COMMENT '科目2名称',
  `km3dm` varchar(20) DEFAULT NULL COMMENT '科目3代码',
  `km3mc` varchar(100) DEFAULT NULL COMMENT '科目3名称',
  `km4dm` varchar(20) DEFAULT NULL COMMENT '科目4代码',
  `km4mc` varchar(100) DEFAULT NULL COMMENT '科目4名称',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_detail` (`zyyjfxdm`),
  KEY `idx_zydm` (`zydm`),
  KEY `idx_dwdm` (`dwdm`),
  KEY `idx_dwmc` (`dwmc`),
  KEY `idx_yxsmc` (`yxsmc`),
  KEY `idx_yjfxmc` (`yjfxmc`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='专业研究方向详情表';

-- 表4：用户表 user
CREATE TABLE IF NOT EXISTS `user` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `hashed_password` varchar(255) NOT NULL COMMENT '哈希后的密码',
  `nickname` varchar(50) DEFAULT NULL COMMENT '昵称',
  `email` varchar(100) DEFAULT NULL COMMENT '邮箱',
  `target_mldm` varchar(10) DEFAULT NULL COMMENT '意向门类代码',
  `target_mlmc` varchar(50) DEFAULT NULL COMMENT '意向门类名称',
  `target_provinces` text DEFAULT NULL COMMENT '意向省市列表(JSON数组)',
  `degree_type` varchar(10) DEFAULT NULL COMMENT '学位期望: xs/zy',
  `study_mode` varchar(10) DEFAULT NULL COMMENT '学习方式期望: 1全日制/2非全日制',
  `self_rating` varchar(10) DEFAULT NULL COMMENT '实力自评: weak/medium/strong',
  `profile_completed` int DEFAULT 0 COMMENT '画像是否完成: 0未完成/1已完成',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 表5：用户收藏表 favorite
CREATE TABLE IF NOT EXISTS `favorite` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `dwdm` varchar(20) NOT NULL COMMENT '院校代码',
  `dwmc` varchar(200) DEFAULT NULL COMMENT '院校名称',
  `zydm` varchar(20) NOT NULL COMMENT '专业代码',
  `zymc` varchar(100) DEFAULT NULL COMMENT '专业名称',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_fav` (`user_id`, `dwdm`, `zydm`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户收藏表';

-- 表6：推荐记录表 recommend_log
CREATE TABLE IF NOT EXISTS `recommend_log` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `zydm` varchar(20) NOT NULL COMMENT '推荐使用的专业代码',
  `dwdm` varchar(20) NOT NULL COMMENT '被推荐的院校代码',
  `dwmc` varchar(200) DEFAULT NULL COMMENT '被推荐的院校名称',
  `score` float DEFAULT NULL COMMENT '推荐得分',
  `tier` varchar(20) DEFAULT NULL COMMENT '推荐层级: sprint/stable/safe',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '推荐时间',
  `request_params` text DEFAULT NULL COMMENT '请求参数快照(JSON)',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='推荐记录表';
