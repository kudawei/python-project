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

-- ============================================================
-- 测试数据：用户表
-- 所有测试用户密码均为: 123456
-- bcrypt 哈希值: $2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y
-- ============================================================

INSERT INTO `user` (`username`, `hashed_password`, `nickname`, `email`, `target_mldm`, `target_mlmc`, `target_provinces`, `degree_type`, `study_mode`, `self_rating`, `profile_completed`, `created_at`) VALUES
-- 用户1：张三，工学，想去北京上海，学术学位，全日制，实力较强
('zhangsan', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '张三', 'zhangsan@example.com', '08', '工学', '["北京市","上海市"]', 'xs', '1', 'strong', 1, '2025-09-01 08:30:00'),

-- 用户2：李四，管理学，想去广东浙江，专业学位，全日制，实力中等
('lisi', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '李四', 'lisi@example.com', '12', '管理学', '["广东省","浙江省"]', 'zy', '1', 'medium', 1, '2025-09-05 10:15:00'),

-- 用户3：王五，经济学，想去北京江苏，学术学位，全日制，实力较弱
('wangwu', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '王五', 'wangwu@example.com', '02', '经济学', '["北京市","江苏省"]', 'xs', '1', 'weak', 1, '2025-09-10 14:00:00'),

-- 用户4：赵六，法学，想去北京，专业学位，非全日制，实力中等
('zhaoliu', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '赵六', 'zhaoliu@example.com', '03', '法学', '["北京市"]', 'zy', '2', 'medium', 1, '2025-09-15 09:20:00'),

-- 用户5：孙七，教育学，想去湖北四川，学术学位，全日制，实力较强
('sunqi', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '孙七', 'sunqi@example.com', '04', '教育学', '["湖北省","四川省"]', 'xs', '1', 'strong', 1, '2025-09-20 11:45:00'),

-- 用户6：周八，文学，想去北京上海浙江，学术学位，全日制，实力中等
('zhouba', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '周八', 'zhouba@example.com', '05', '文学', '["北京市","上海市","浙江省"]', 'xs', '1', 'medium', 1, '2025-10-01 08:00:00'),

-- 用户7：吴九，理学，想去北京天津，学术学位，全日制，实力较强
('wujiu', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '吴九', 'wujiu@example.com', '07', '理学', '["北京市","天津市"]', 'xs', '1', 'strong', 1, '2025-10-05 13:30:00'),

-- 用户8：郑十，医学，想去上海广东，专业学位，全日制，实力中等
('zhengshi', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '郑十', 'zhengshi@example.com', '10', '医学', '["上海市","广东省"]', 'zy', '1', 'medium', 1, '2025-10-10 16:00:00'),

-- 用户9：陈一一，艺术学，想去北京四川，学术学位，全日制，实力较弱
('chenyiyi', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '陈一一', 'chenyiyi@example.com', '13', '艺术学', '["北京市","四川省"]', 'xs', '1', 'weak', 1, '2025-10-15 10:10:00'),

-- 用户10：林二二，哲学，想去北京，学术学位，全日制，实力较强
('linerer', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '林二二', 'linerer@example.com', '01', '哲学', '["北京市"]', 'xs', '1', 'strong', 1, '2025-10-20 09:00:00'),

-- 用户11：黄三三，历史学，想去上海江苏，学术学位，全日制，实力中等
('huangss', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '黄三三', 'huangss@example.com', '06', '历史学', '["上海市","江苏省"]', 'xs', '1', 'medium', 1, '2025-10-25 14:30:00'),

-- 用户12：杨四四，农学，想去北京湖北，学术学位，全日制，实力较弱
('yangss', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '杨四四', 'yangss@example.com', '09', '农学', '["北京市","湖北省"]', 'xs', '1', 'weak', 1, '2025-11-01 08:45:00'),

-- 用户13：刘五五，工学，想去广东深圳，专业学位，非全日制，实力中等
('liuww', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '刘五五', 'liuww@example.com', '08', '工学', '["广东省"]', 'zy', '2', 'medium', 1, '2025-11-05 11:00:00'),

-- 用户14：何六六，管理学，想去北京上海广东，专业学位，全日制，实力较强
('helliu', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '何六六', 'helliu@example.com', '12', '管理学', '["北京市","上海市","广东省"]', 'zy', '1', 'strong', 1, '2025-11-10 15:20:00'),

-- 用户15：马七七，经济学，想去浙江江苏，学术学位，全日制，实力中等
('maqq', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '马七七', 'maqq@example.com', '02', '经济学', '["浙江省","江苏省"]', 'xs', '1', 'medium', 1, '2025-11-15 09:30:00'),

-- 用户16：高八八，法学，想去北京上海，学术学位，全日制，实力较强（画像未完成）
('gaobb', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '高八八', 'gaobb@example.com', NULL, NULL, NULL, NULL, NULL, NULL, 0, '2025-11-20 10:00:00'),

-- 用户17：罗九九，新注册用户（画像未完成）
('luojj', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '罗九九', 'luojj@example.com', NULL, NULL, NULL, NULL, NULL, NULL, 0, '2025-11-25 16:40:00'),

-- 用户18：谢十十，工学，想去天津辽宁，学术学位，全日制，实力较弱
('xiess', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '谢十十', 'xiess@example.com', '08', '工学', '["天津市","辽宁省"]', 'xs', '1', 'weak', 1, '2025-12-01 08:15:00'),

-- 用户19：韩冬冬，教育学，想去湖南福建，专业学位，全日制，实力中等
('handd', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '韩冬冬', 'handd@example.com', '04', '教育学', '["湖南省","福建省"]', 'zy', '1', 'medium', 1, '2025-12-05 13:50:00'),

-- 用户20：唐春春，医学，想去北京上海广东四川，专业学位，全日制，实力较强
('tangcc', '$2b$12$yW/qkJfkPZgW1RGucu2VFe63Skys2.nygToaQlhCxIigPtQtLrS8y', '唐春春', 'tangcc@example.com', '10', '医学', '["北京市","上海市","广东省","四川省"]', 'zy', '1', 'strong', 1, '2025-12-10 10:30:00');

-- 测试用户登录说明：
-- 所有用户的登录密码均为: 123456
-- 用户16(高八八)和用户17(罗九九)的画像未完成，可用于测试画像填写流程
-- 其余用户画像已完成，覆盖了不同的门类、省市、学位类型、学习方式和实力自评组合
