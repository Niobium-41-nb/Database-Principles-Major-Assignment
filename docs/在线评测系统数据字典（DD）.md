# 在线评测系统数据字典（DD）

## 1. 数据流定义

### 1.1 用户相关数据流

| 数据流名称 | 来源 | 目的地 | 组成 | 频率 | 说明 |
|-----------|------|--------|------|------|------|
| **用户注册信息** | 用户界面 | 认证模块 | `用户名(handle) + 邮箱(email) + 密码(password) + 姓名(name)` | 低频 | 新用户注册信息 |
| **用户登录信息** | 用户界面 | 认证模块 | `用户名(handle) + 密码(password)` | 高频 | 用户登录凭证 |
| **用户个人信息** | 用户管理 | 用户界面 | `用户ID + 用户名 + 邮箱 + 姓名 + Rating + 排名 + 国家 + 组织 + 注册时间 + 管理员标志` | 中频 | 用户完整信息 |
| **用户资料更新** | 用户界面 | 用户管理 | `用户ID + 姓名 + 国家 + 城市 + 组织 + 头像` | 低频 | 用户资料修改 |

### 1.2 题目相关数据流

| 数据流名称 | 来源 | 目的地 | 组成 | 频率 | 说明 |
|-----------|------|--------|------|------|------|
| **题目列表查询** | 用户界面 | 题目管理 | `页码 + 每页数量 + 筛选条件(难度/标签)` | 高频 | 获取题目列表 |
| **题目详情查询** | 用户界面 | 题目管理 | `题目ID(problem_id)` | 高频 | 获取题目详细信息 |
| **题目统计信息** | 题目管理 | 用户界面 | `题目ID + 标题 + 难度 + 提交数 + 通过数 + 时间限制 + 内存限制` | 高频 | 题目统计数据 |
| **题目创建信息** | 管理员界面 | 题目管理 | `题目ID + 标题 + 描述 + 输入输出规范 + 时间限制 + 内存限制 + 标签列表 + 测试用例` | 低频 | 创建新题目 |

### 1.3 提交评测数据流

| 数据流名称 | 来源 | 目的地 | 组成 | 频率 | 说明 |
|-----------|------|--------|------|------|------|
| **代码提交** | 用户界面 | 提交评测 | `用户ID + 题目ID + 编程语言 + 源代码 + 提交时间` | 高频 | 用户提交解题代码 |
| **评测结果** | 代码执行 | 用户界面 | `提交ID + 评测状态 + 用时 + 内存 + 通过测试数 + 得分` | 高频 | 代码执行结果 |
| **提交记录查询** | 用户界面 | 提交管理 | `用户句柄 + 题目标题 + 评测状态 + 时间范围` | 中频 | 查询提交历史 |
| **实时评测状态** | 评测队列 | 用户界面 | `提交ID + 当前状态 + 进度百分比` | 高频 | 评测过程状态更新 |

### 1.4 比赛相关数据流

| 数据流名称 | 来源 | 目的地 | 说明 |
|-----------|------|--------|------|
| **比赛列表查询** | 用户界面 → 比赛管理 | 获取所有可见比赛 |
| **比赛详情查询** | 用户界面 → 比赛管理 | 获取特定比赛详细信息 |
| **比赛报名信息** | 用户界面 → 比赛管理 | 用户报名参加比赛 |
| **比赛排名数据** | 排名管理 → 用户界面 | 实时比赛排名信息 |
| **比赛创建信息** | 管理员界面 → 比赛管理 | 创建新比赛 |

### 1.5 Hack相关数据流

| 数据流名称 | 来源 | 目的地 | 组成 | 频率 | 说明 |
|-----------|------|--------|------|------|------|
| **Hack提交** | 用户界面 | Hack管理 | `黑客ID + 提交ID + 测试输入 + 预期输出` | 中频 | 提交Hack数据 |
| **Hack结果** | Hack管理 | 用户界面 | `HackID + 结果状态 + 详细信息 + Rating变化` | 中频 | Hack执行结果 |
| **Hack记录查询** | 用户界面 | Hack管理 | `时间范围 + 参与者 + 问题` | 低频 | 查询Hack历史 |

## 2. 数据存储定义

### 2.1 Users（用户表）

```sql
数据存储：Users
别名：用户信息表
描述：存储系统所有用户的基本信息和评级数据
组成：{
    user_id: BIGINT IDENTITY(1,1) PRIMARY KEY,
    handle: VARCHAR(50) UNIQUE NOT NULL,
    email: VARCHAR(100) UNIQUE NOT NULL,
    password: VARCHAR(255) NOT NULL,
    name: VARCHAR(100),
    rating: INT DEFAULT 0,
    max_rating: INT DEFAULT 0,
    user_rank: VARCHAR(50) DEFAULT 'Newbie',
    max_rank: VARCHAR(50) DEFAULT 'Newbie',
    country: VARCHAR(100),
    city: VARCHAR(100),
    organization: VARCHAR(200),
    avatar: VARCHAR(500),
    registration_time: DATETIME2 DEFAULT GETDATE(),
    last_online_time: DATETIME2 DEFAULT GETDATE(),
    contribution: INT DEFAULT 0,
    is_admin: BIT DEFAULT 0,
    is_active: BIT DEFAULT 1
}
索引：{
    idx_user_rating (rating),
    idx_user_handle (handle),
    idx_user_rank (user_rank)
}
访问频率：高频读取，中频更新（Rating、最后在线时间）
数据量：预计1000-10000条记录
```

### 2.2 PROBLEM（题目表）

```sql
数据存储：PROBLEM
别名：题目信息表
描述：存储所有题目的基本信息、限制条件和内容
组成：{
    problem_id: VARCHAR(50) PRIMARY KEY,
    contest_id: BIGINT FOREIGN KEY REFERENCES CONTEST(contest_id),
    problem_index: VARCHAR(10),
    title: VARCHAR(300) NOT NULL,
    statement: TEXT,
    input_specification: TEXT,
    output_specification: TEXT,
    sample_tests: NVARCHAR(MAX),
    notes: TEXT,
    time_limit_ms: INT NOT NULL DEFAULT 1000,
    memory_limit_kb: INT NOT NULL DEFAULT 256000,
    difficulty: VARCHAR(10),
    creation_time: DATETIME2 DEFAULT GETDATE(),
    is_visible: BIT DEFAULT 1
}
索引：{
    idx_problem_contest (contest_id),
    idx_problem_difficulty (difficulty)
}
访问频率：高频读取，低频更新
数据量：预计500-2000条记录
```

### 2.3 SUBMISSION（提交表）

```sql
数据存储：SUBMISSION
别名：提交记录表
描述：存储用户的所有代码提交记录和评测结果
组成：{
    submission_id: BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id: BIGINT NOT NULL FOREIGN KEY REFERENCES Users(user_id),
    problem_id: VARCHAR(50) NOT NULL FOREIGN KEY REFERENCES PROBLEM(problem_id),
    contest_id: BIGINT FOREIGN KEY REFERENCES CONTEST(contest_id),
    programming_language: VARCHAR(50) NOT NULL,
    source_code: TEXT NOT NULL,
    source_length: INT NOT NULL,
    verdict: VARCHAR(50) DEFAULT 'Pending' CHECK (
        verdict IN ('Pending', 'Running', 'Accepted', 'Wrong Answer', 
                   'Time Limit Exceeded', 'Memory Limit Exceeded', 'Runtime Error',
                   'Compilation Error', 'Presentation Error', 'Failed',
                   'Idleness Limit Exceeded', 'Partial Solution', 'Skipped',
                   'Challenged', 'Rejected')
    ),
    time_consumed_ms: INT DEFAULT 0,
    memory_consumed_kb: INT DEFAULT 0,
    passed_test_count: INT DEFAULT 0,
    test_results: NVARCHAR(MAX),
    submission_time: DATETIME2 DEFAULT GETDATE(),
    relative_time: INT,
    points: INT
}
索引：{
    idx_submission_user_time (user_id, submission_time),
    idx_submission_contest (contest_id, problem_id),
    idx_submission_verdict (verdict),
    idx_submission_problem_verdict (problem_id, verdict)
}
访问频率：极高频写入和读取
数据量：预计10万-100万条记录，需要定期归档
```

### 2.4 CONTEST（比赛表）

```sql
数据存储：CONTEST
别名：比赛信息表
描述：存储所有比赛的基本信息和配置
组成：{
    contest_id: BIGINT IDENTITY(1,1) PRIMARY KEY,
    name: VARCHAR(200) NOT NULL,
    type: VARCHAR(10) NOT NULL DEFAULT 'CF' CHECK (type IN ('CF', 'IOI', 'ICPC')),
    phase: VARCHAR(30) DEFAULT 'BEFORE' CHECK (
        phase IN ('BEFORE', 'CODING', 'PENDING_SYSTEM_TEST', 'SYSTEM_TEST', 'FINISHED')
    ),
    frozen: BIT DEFAULT 0,
    start_time: DATETIME2 NOT NULL,
    duration_seconds: INT NOT NULL,
    website_url: VARCHAR(500),
    description: TEXT,
    difficulty: INT DEFAULT 0,
    kind: VARCHAR(100),
    icpc_region: VARCHAR(100),
    country: VARCHAR(100),
    city: VARCHAR(100),
    season: VARCHAR(50),
    created_by: BIGINT FOREIGN KEY REFERENCES Users(user_id)
}
索引：{
    idx_contest_time (start_time),
    idx_contest_type (type)
}
访问频率：中频读取，低频更新
数据量：预计100-500条记录
```

### 2.5 HACK（Hack记录表）

```sql
数据存储：HACK
别名：Hack记录表
描述：存储用户之间的Hack记录和结果
组成：{
    hack_id: BIGINT IDENTITY(1,1) PRIMARY KEY,
    hacker_id: BIGINT NOT NULL FOREIGN KEY REFERENCES Users(user_id),
    submission_id: BIGINT NOT NULL FOREIGN KEY REFERENCES SUBMISSION(submission_id),
    verdict: VARCHAR(20) NOT NULL CHECK (verdict IN ('SUCCESSFUL', 'UNSUCCESSFUL', 'INVALID')),
    test_case: TEXT NOT NULL,
    hack_time: DATETIME2 DEFAULT GETDATE(),
    hack_result: TEXT
}
索引：{
    idx_hack_time (hack_time),
    idx_hack_verdict (verdict),
    idx_hack_submission (submission_id)
}
访问频率：中频读写
数据量：预计1万-5万条记录
```

### 2.6 CONTEST_USER（比赛用户关系表）

```sql
数据存储：CONTEST_USER
别名：比赛用户关系表
描述：存储用户参加比赛的信息和比赛结果
组成：{
    contest_id: BIGINT NOT NULL FOREIGN KEY REFERENCES CONTEST(contest_id),
    user_id: BIGINT NOT NULL FOREIGN KEY REFERENCES Users(user_id),
    registration_time: DATETIME2 DEFAULT GETDATE(),
    role: VARCHAR(30) NOT NULL DEFAULT 'contestant' CHECK (
        role IN ('author', 'tester', 'contestant', 'out_of_competition', 'virtual')
    ),
    rating_before: INT,
    rating_after: INT,
    contest_rank: INT,
    solved_count: INT DEFAULT 0,
    total_penalty: INT DEFAULT 0,
    scores: INT DEFAULT 0,
    PRIMARY KEY (contest_id, user_id)
}
索引：{
    idx_contest_user_role (role)
}
访问频率：比赛期间高频读写
数据量：预计1万-5万条记录
```

### 2.7 其他数据存储

#### PROBLEM_TAG（题目标签表）
```sql
数据存储：PROBLEM_TAG
组成：标签ID + 标签名 + 描述
数据量：预计50-100条记录
```

#### PROBLEM_TAG_RELATION（题目标签关系表）
```sql
数据存储：PROBLEM_TAG_RELATION  
组成：问题ID + 标签ID（复合主键）
数据量：预计1000-5000条记录
```

#### TEST_CASE（测试用例表）
```sql
数据存储：TEST_CASE
组成：测试用例ID + 问题ID + 输入数据 + 期望输出 + 是否样例 + 测试顺序
数据量：预计1万-5万条记录
```

## 3. 处理过程定义

### 3.1 用户认证处理

| 过程名称 | 输入 | 输出 | 处理逻辑 |
|---------|------|------|----------|
| **用户注册** | 注册信息表单 | 注册结果 | `验证信息完整性 → 检查用户名/邮箱唯一性 → 密码加密 → 创建用户记录 → 初始化Rating和排名 → 返回成功/失败` |
| **用户登录** | 登录凭证 | 登录结果 | `验证凭证有效性 → 更新最后在线时间 → 建立用户会话 → 返回用户信息和权限` |
| **权限验证** | 用户请求 | 权限结果 | `检查会话有效性 → 验证用户权限 → 记录操作日志 → 允许/拒绝访问` |

### 3.2 题目管理处理

| 过程名称 | 输入 | 输出 | 处理逻辑 |
|---------|------|------|----------|
| **题目创建** | 题目数据 | 创建结果 | `验证管理员权限 → 生成题目ID → 存储题目信息 → 创建测试用例 → 设置题目标签 → 返回创建结果` |
| **题目查询** | 查询条件 | 题目列表 | `构建查询语句 → 获取题目数据 → 计算统计信息 → 格式化返回数据` |
| **题目统计** | 题目ID | 统计数据 | `查询提交记录 → 计算通过率 → 更新缓存 → 返回统计结果` |

### 3.3 代码评测处理

| 过程名称 | 输入 | 输出 | 处理逻辑 |
|---------|------|------|----------|
| **代码提交** | 提交数据 | 提交结果 | `验证用户权限 → 检查提交频率 → 存储源代码 → 加入评测队列 → 返回提交ID` |
| **代码评测** | 提交ID | 评测结果 | `获取提交信息 → 编译代码 → 执行测试用例 → 比较输出结果 → 记录评测详情 → 更新题目统计` |
| **结果通知** | 评测结果 | 用户通知 | `推送评测状态 → 更新用户界面 → 记录评测日志 → 触发相关事件` |

### 3.4 比赛管理处理

| 过程名称 | 输入 | 输出 | 处理逻辑 |
|---------|------|------|----------|
| **比赛创建** | 比赛配置 | 创建结果 | `验证管理员权限 → 设置比赛参数 → 创建比赛记录 → 初始化排名系统 → 返回比赛ID` |
| **比赛报名** | 报名请求 | 报名结果 | `验证比赛状态 → 检查用户资格 → 记录报名信息 → 初始化比赛数据 → 返回报名结果` |
| **排名计算** | 提交数据 | 实时排名 | `收集用户提交 → 计算解题数和罚时 → 应用比赛规则 → 生成排名列表 → 更新排名显示` |

### 3.5 Hack处理

| 过程名称 | 输入 | 输出 | 处理逻辑 |
|---------|------|------|----------|
| **Hack提交** | Hack数据 | Hack结果 | `验证Hack权限 → 检查提交状态 → 执行Hack测试 → 判定Hack结果 → 更新用户Rating → 记录Hack详情` |
| **Hack验证** | 测试数据 | 验证结果 | `运行目标代码 → 比较输出结果 → 判定是否成功 → 返回验证详情` |

## 4. 外部实体定义

### 4.1 系统用户

| 实体名称 | 输出数据流 | 输入数据流 | 说明 |
|---------|-----------|-----------|------|
| **普通用户** | 代码提交、题目查询、比赛报名 | 评测结果、比赛信息、排名更新 | 系统主要使用者，参与解题和比赛 |
| **管理员用户** | 题目创建、比赛管理、用户管理 | 系统状态、操作结果 | 系统维护者，拥有高级权限 |
| **比赛参与者** | 比赛提交、Hack操作 | 实时排名、比赛通知 | 专门参与比赛的用户 |

### 4.2 外部系统

| 实体名称 | 输出数据流 | 输入数据流 | 说明 |
|---------|-----------|-----------|------|
| **SQL Server数据库** | 查询结果、状态信息 | SQL操作、数据存储 | 系统数据持久化存储 |
| **代码执行引擎** | 执行结果、错误信息 | 源代码、测试用例 | 独立代码评测服务 |
| **前端Web界面** | 用户操作、表单提交 | 页面数据、状态更新 | 用户交互界面 |
