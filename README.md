> 数据库原理实验：课程考核是分小组完成一个数据库设计大作业，每个小组2人，需要从选题、需求分析开始分阶段完成一个数据库应用程序的设计与实现，课程结束需要进行演示答辩并提交设计报告和源程序。课程设计大作业占总成绩的70%，过程考核（实验作业、考勤和课堂表现）占总成绩的30%。

# 数据库设计

这是一个为在线判题系统（OJ）设计的数据库，特别是模仿 **Codeforces** 平台的功能和结构。数据库名为 `OJ`，使用 **Microsoft SQL Server** 语法编写。下面是对该数据库的详细介绍：

---

## [数据库结构概览](docs\数据库结构概览.md)

该数据库包含以下主要表结构：

### 1. **用户表 (`USER`)**

存储用户信息，包括：

- 用户ID、用户名（handle）、邮箱、密码
- 评分相关：当前评分、最高评分、当前等级、最高等级
- 个人信息：国家、城市、组织、头像
- 活跃信息：注册时间、最后在线时间、贡献值
- 权限标记：是否为管理员、是否活跃

### 2. **比赛表 (`CONTEST`)**

存储比赛信息：

- 比赛ID、名称、类型（CF/IOI/ICPC）、阶段（BEFORE/FINISHED等）
- 时间信息：开始时间、持续时间（秒）
- 描述信息：网址、描述、难度、类型、ICPC区域等
- 创建者外键关联用户

### 3. **题目表 (`PROBLEM`)**

存储题目详情：

- 题目ID（唯一）、所属比赛、题目索引（如A、B、C）
- 题目内容：标题、题目描述、输入输出规范、样例
- 限制条件：时间限制、内存限制
- 统计信息：通过数、提交数、难度
- 可见性控制

### 4. **题目标签系统**

- `PROBLEM_TAG`：标签字典表
- `PROBLEM_TAG_RELATION`：题目与标签的多对多关系表

### 5. **测试用例表 (`TEST_CASE`)**

存储题目的测试数据：

- 输入数据、期望输出
- 标记是否为样例、测试顺序

### 6. **提交表 (`SUBMISSION`)**

记录用户提交：

- 提交ID、用户ID、题目ID、比赛ID
- 编程语言、源代码、代码长度
- 判题结果：状态（AC/WRONG_ANSWER等）、耗时、内存使用
- 通过测试数、详细测试结果、提交时间

### 7. **比赛用户关系表 (`CONTEST_USER`)**

记录用户参与比赛的情况：

- 用户在比赛中的角色（作者/测试者/参赛者等）
- 比赛前后的评分变化
- 比赛排名、解题数、罚分、得分

### 8. **Hack表 (`HACK`)**

记录Hack行为：

- Hack者、被Hack者、题目、比赛
- Hack结果（成功/失败/无效）
- 使用的测试用例、Hack时间、结果详情

## [功能实现](docs\功能实现.md)

### 查询

1.对所有用户公开信息的查询：
  
2.对所有比赛的信息查询

3.支持对所有题目的信息查询

4.支持对所有提交记录的信息查询

5.对某比赛排名情况的排名

### 修改

1.注册账号
  - 在用户表中添加用户信息
  
2.出题
  - 在题目表中添加题目信息

3.提交
  - 在提交表中添加提交信息，评测结果用随机。


基于你们的技术栈（前端：HTML/CSS/JS，后端：Python），我推荐使用 **Flask** 作为后端框架，因为它轻量、易上手，且与前端配合简单。以下是完整的项目框架设计：

---

# 🗂️ 项目文件夹结构

```
OnlineJudge/
├── backend/                 # 后端 Flask 应用
│   ├── app.py              # Flask 主程序入口
│   ├── models.py           # 数据库模型（SQLAlchemy）
│   ├── database.py         # 数据库连接与初始化
│   ├── routes/             # 路由模块
│   │   ├── user_routes.py
│   │   ├── problem_routes.py
│   │   ├── contest_routes.py
│   │   └── submission_routes.py
│   ├── utils/              # 工具函数
│   │   ├── judge.py        # 模拟评测逻辑（随机结果）
│   │   └── auth.py         # 认证相关
│   ├── config.py           # 配置文件
│   └── requirements.txt    # Python 依赖包
│
├── frontend/               # 前端静态文件
│   ├── index.html          # 首页
│   ├── css/
│   │   └── style.css       # 全局样式
│   ├── js/
│   │   ├── main.js         # 主逻辑
│   │   ├── user.js         # 用户相关功能
│   │   ├── problem.js      # 题目展示与提交
│   │   ├── contest.js      # 比赛列表与排名
│   │   └── submission.js   # 提交记录查询
│   └── assets/             # 图片、图标等静态资源
│
├── docs/                   # 项目文档
│   ├── README.md
│   ├── 功能实现.md
│   └── 数据库结构概览.md
│
└── README.md               # 项目总说明
```

---

# 🛠️ 技术栈说明

### [后端（Python + Flask）](docs/后端开发手册.md)
- **Flask**：轻量级 Web 框架
- **SQLAlchemy**：ORM 数据库操作
- **PyMySQL / pymssql**：连接 SQL Server
- **Flask-CORS**：处理前端跨域请求

### [前端（HTML + CSS + JS）](docs/前端开发手册.md)
- 原生 JavaScript + Fetch API 与后端交互
- CSS 使用 Flex/Grid 布局，响应式设计
- 无需框架，便于快速上手和部署

---

## 📦 环境与依赖

### `backend/requirements.txt`
```txt
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-CORS==4.0.0
pymssql==2.2.7
```

---

## 🚀 快速开始

### 1. 克隆项目并安装后端依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置数据库连接
在 `backend/config.py` 中修改：
```python
SQLALCHEMY_DATABASE_URI = "mssql+pymssql://用户名:密码@服务器地址/数据库名"
```

### 3. 启动后端
```bash
python app.py
```

### 4. 启动前端
用浏览器打开 `frontend/index.html`，或使用 Live Server（VSCode 插件）启动。

---
