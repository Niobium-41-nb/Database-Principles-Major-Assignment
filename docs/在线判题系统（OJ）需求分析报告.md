# 在线判题系统（OJ）需求分析报告

## 1. 用户的信息、处理和安全性完整性需求

| **角色**       | **权限描述**                                               | **安全要求**                                                 |
| -------------- | ---------------------------------------------------------- | ------------------------------------------------------------ |
| **普通用户**   | **注册、登录、浏览题目、提交代码、查看个人提交、参与讨论** | **密码加密存储，Token身份验证，提交频率限制（每分钟≤10次），个人数据隐私保护** |
| **参赛者**     | **参与比赛、实时排名、查看比赛题目**                       | **比赛期间IP监控，禁止多账号参赛，代码查重检测，比赛数据隔离保护** |
| **题目管理员** | **创建题目、设置测试用例、管理题目分类**                   | **操作日志全记录，权限分级管理，题目版本控制，敏感操作二次确认** |
| **系统管理员** | **用户管理、系统配置、数据备份、监控系统状态**             | **双因素身份认证，操作审计追踪，敏感操作确认机制，数据完整性校验** |

**处理需求与安全约束对应表**

| **处理需求**     | **安全完整性措施**                            | **数据保护要求**                             |
| ---------------- | --------------------------------------------- | -------------------------------------------- |
| **用户注册登录** | **密码强度校验，登录失败锁定，Token超时控制** | **密码哈希存储，登录日志记录，防暴力破解**   |
| **代码提交判题** | **提交频率限制，代码安全检查，运行环境隔离**  | **代码内容过滤，沙箱环境运行，资源使用监控** |
| **比赛参与排名** | **身份真实性验证，作弊行为检测，公平性保障**  | **比赛数据加密，排名计算透明，防篡改保护**   |
| **题目管理维护** | **操作权限控制，修改记录追踪，版本管理**      | **测试用例加密，操作日志存档，数据备份机制** |
| **系统管理维护** | **管理员身份强认证，操作流程规范化**          | **系统配置备份，操作审计完整，灾难恢复预案** |

## 2. 文档清单

| **文档序号** | **文档名称**   | **处理及存档要求**                                           |
| ------------ | -------------- | ------------------------------------------------------------ |
| **1**        | **用户信息表** | **更新频率：实时更新用户提交统计，每月生成用户活跃报告。数据准确性：用户积分需与提交记录严格一致。权限管理：普通用户仅查看公开信息，管理员可查看全部。** |
| **2**        | **题目信息表** | **更新频率：题目发布时更新，每月统计题目通过率。数据准确性：测试用例输入输出需经过验证。特殊标注：高难度题目需特殊标记，比赛题目需设置可见性。** |
| **3**        | **提交记录表** | **更新频率：每次提交实时更新，每日归档历史记录。数据准确性：判题结果需与测试用例严格匹配。权限管理：用户仅查看自己提交记录，比赛期间部分隐藏。** |
| **4**        | **比赛信息表** | **更新频率：赛前配置，赛中实时更新排名，赛后生成统计报告。数据准确性：比赛时间同步，排名计算准确。权限管理：公开比赛全员可见，私有比赛密码保护。** |
| **5**        | **测试用例表** | **更新频率：题目创建时设置，重大更新时修订。数据安全性：测试用例加密存储，访问日志记录。完整性要求：MD5校验防止篡改。** |

## 3.数据项清单

| **局部序号** | **数据项名称(英文)**  | **数据项名称(中文)** | **全局序号** | **数据项名称(英文)**  | **数据项名称(中文)** | **对应文档序号** |
| ------------ | --------------------- | -------------------- | ------------ | --------------------- | -------------------- | ---------------- |
| **1_1**      | **user_id**           | **用户ID**           | **1**        | **user_id**           | **用户ID**           | **1**            |
| **1_2**      | **handle**            | **用户名**           | **2**        | **handle**            | **用户名**           | **1**            |
| **1_3**      | **email**             | **邮箱**             | **3**        | **email**             | **邮箱**             | **1**            |
| **1_4**      | **password**          | **密码**             | **4**        | **password**          | **密码**             | **1**            |
| **1_5**      | **name**              | **姓名**             | **5**        | **name**              | **姓名**             | **1**            |
| **1_6**      | **rating**            | **当前评分**         | **6**        | **rating**            | **当前评分**         | **1**            |
| **1_7**      | **max_rating**        | **最高评分**         | **7**        | **max_rating**        | **最高评分**         | **1**            |
| **1_8**      | **user_rank**         | **当前等级**         | **8**        | **user_rank**         | **当前等级**         | **1**            |
| **1_9**      | **max_rank**          | **最高等级**         | **9**        | **max_rank**          | **最高等级**         | **1**            |
| **1_10**     | **registration_time** | **注册时间**         | **10**       | **registration_time** | **注册时间**         | **1**            |
| **1_11**     | **last_online_time**  | **最后在线时间**     | **11**       | **last_online_time**  | **最后在线时间**     | **1**            |
| **2_1**      | **problem_id**        | **题目ID**           | **12**       | **problem_id**        | **题目ID**           | **2**            |
| **2_2**      | **contest_id**        | **比赛ID**           | **13**       | **contest_id**        | **比赛ID**           | **2**            |
| **2_3**      | **title**             | **题目标题**         | **14**       | **title**             | **题目标题**         | **2**            |
| **2_4**      | **statement**         | **题目描述**         | **15**       | **statement**         | **题目描述**         | **2**            |
| **2_5**      | **time_limit_ms**     | **时间限制**         | **16**       | **time_limit_ms**     | **时间限制**         | **2**            |
| **2_6**      | **memory_limit_kb**   | **内存限制**         | **17**       | **memory_limit_kb**   | **内存限制**         | **2**            |
| **2_7**      | **difficulty**        | **难度等级**         | **18**       | **difficulty**        | **难度等级**         | **2**            |
| **3_1**      | **submission_id**     | **提交ID**           | **19**       | **submission_id**     | **提交ID**           | **3**            |
| **3_2**      | **programming_language** | **编程语言**      | **20**       | **programming_language** | **编程语言**      | **3**            |
| **3_3**      | **source_code**       | **源代码**           | **21**       | **source_code**       | **源代码**           | **3**            |
| **3_4**      | **verdict**           | **评测结果**         | **22**       | **verdict**           | **评测结果**         | **3**            |
| **3_5**      | **time_consumed_ms**  | **运行时间**         | **23**       | **time_consumed_ms**  | **运行时间**         | **3**            |
| **4_1**      | **contest_id**        | **比赛ID**           | **13**       | **contest_id**        | **比赛ID**           | **4**            |
| **4_2**      | **name**              | **比赛名称**         | **24**       | **name**              | **比赛名称**         | **4**            |
| **4_3**      | **type**              | **比赛类型**         | **25**       | **type**              | **比赛类型**         | **4**            |
| **4_4**      | **start_time**        | **开始时间**         | **26**       | **start_time**        | **开始时间**         | **4**            |

## 4. 数据库结构概览

### 4.1 数据库基本信息

| **配置项**     | **规格说明**                    |
| -------------- | ------------------------------- |
| **数据库名称** | **OJ**                          |
| **数据库类型** | **Microsoft SQL Server**        |
| **认证方式**   | **Windows 身份验证**            |
| **字符编码**   | **UTF-8**                       |
| **并发支持**   | **支持1000+并发用户**           |
| **备份策略**   | **每日完整备份 + 事务日志备份** |

## 4.2 主要数据表结构

### **用户表 (Users) - 存储系统所有用户信息**

| **字段名**            | **数据类型**     | **约束**                       | **说明**                     |
| --------------------- | ---------------- | ------------------------------ | ---------------------------- |
| **user_id**           | **BIGINT**       | **PRIMARY KEY, IDENTITY(1,1)** | **用户唯一标识**             |
| **handle**            | **VARCHAR(50)**  | **UNIQUE, NOT NULL**           | **用户名（唯一）**           |
| **email**             | **VARCHAR(100)** | **UNIQUE, NOT NULL**           | **邮箱地址**                 |
| **password**          | **VARCHAR(255)** | **NOT NULL**                   | **加密密码**                 |
| **name**              | **VARCHAR(100)** | -                              | **真实姓名**                 |
| **rating**            | **INT**          | **DEFAULT 0**                  | **当前评分**                 |
| **max_rating**        | **INT**          | **DEFAULT 0**                  | **历史最高评分**             |
| **user_rank**         | **VARCHAR(50)**  | **DEFAULT 'Newbie'**           | **当前等级**                 |
| **max_rank**          | **VARCHAR(50)**  | **DEFAULT 'Newbie'**           | **历史最高等级**             |
| **country**           | **VARCHAR(100)** | -                              | **国家**                     |
| **city**              | **VARCHAR(100)** | -                              | **城市**                     |
| **organization**      | **VARCHAR(200)** | -                              | **组织/学校**                |
| **avatar**            | **VARCHAR(500)** | -                              | **头像URL**                  |
| **registration_time** | **DATETIME2**    | **DEFAULT GETDATE()**          | **注册时间**                 |
| **last_online_time**  | **DATETIME2**    | **DEFAULT GETDATE()**          | **最后在线时间**             |
| **contribution**      | **INT**          | **DEFAULT 0**                  | **贡献值**                   |
| **is_admin**          | **BIT**          | **DEFAULT 0**                  | **管理员标识**               |
| **is_active**         | **BIT**          | **DEFAULT 1**                  | **账户激活状态**             |

**索引设计：**
- `idx_user_rating` - 评分索引
- `idx_user_handle` - 用户名索引  
- `idx_user_rank` - 等级索引

---

### **比赛表 (CONTEST) - 存储比赛相关信息**

| **字段名**           | **数据类型**     | **约束**                                      | **说明**             |
| -------------------- | ---------------- | --------------------------------------------- | -------------------- |
| **contest_id**       | **BIGINT**       | **PRIMARY KEY, IDENTITY(1,1)**                | **比赛唯一标识**     |
| **name**             | **VARCHAR(200)** | **NOT NULL**                                  | **比赛名称**         |
| **type**             | **VARCHAR(10)**  | **DEFAULT 'CF', CHECK IN ('CF','IOI','ICPC')** | **比赛类型**         |
| **phase**            | **VARCHAR(30)**  | **DEFAULT 'BEFORE', CHECK约束**               | **比赛阶段**         |
| **frozen**           | **BIT**          | **DEFAULT 0**                                 | **是否封榜**         |
| **start_time**       | **DATETIME2**    | **NOT NULL**                                  | **开始时间**         |
| **duration_seconds** | **INT**          | **NOT NULL**                                  | **持续时间（秒）**   |
| **website_url**      | **VARCHAR(500)** | -                                             | **比赛网址**         |
| **description**      | **TEXT**         | -                                             | **比赛描述**         |
| **difficulty**       | **INT**          | **DEFAULT 0**                                 | **比赛难度**         |
| **kind**             | **VARCHAR(100)** | -                                             | **比赛种类**         |
| **icpc_region**      | **VARCHAR(100)** | -                                             | **ICPC赛区**         |
| **country**          | **VARCHAR(100)** | -                                             | **举办国家**         |
| **city**             | **VARCHAR(100)** | -                                             | **举办城市**         |
| **season**           | **VARCHAR(50)**  | -                                             | **赛季**             |
| **created_by**       | **BIGINT**       | **FOREIGN KEY**                               | **创建者ID**         |

**索引设计：**
- `idx_contest_time` - 开始时间索引
- `idx_contest_type` - 比赛类型索引

---

### **题目表 (PROBLEM) - 存储题目详细信息**

| **字段名**          | **数据类型**     | **约束**                      | **说明**               |
| ------------------- | ---------------- | ----------------------------- | ---------------------- |
| **problem_id**      | **VARCHAR(50)**  | **PRIMARY KEY**               | **题目ID（唯一）**     |
| **contest_id**      | **BIGINT**       | **FOREIGN KEY**               | **所属比赛ID**         |
| **problem_index**   | **VARCHAR(10)**  | -                             | **题目在比赛中索引**   |
| **title**           | **VARCHAR(300)** | **NOT NULL**                  | **题目标题**           |
| **statement**       | **TEXT**         | -                             | **题目描述**           |
| **input_specification** | **TEXT**     | -                             | **输入规范**           |
| **output_specification** | **TEXT**    | -                             | **输出规范**           |
| **sample_tests**    | **NVARCHAR(MAX)** | -                            | **样例测试**           |
| **notes**           | **TEXT**         | -                             | **备注**               |
| **time_limit_ms**   | **INT**          | **DEFAULT 1000**              | **时间限制（毫秒）**   |
| **memory_limit_kb** | **INT**          | **DEFAULT 256000**            | **内存限制（KB）**     |
| **difficulty**      | **VARCHAR(10)**  | -                             | **难度等级**           |
| **creation_time**   | **DATETIME2**    | **DEFAULT GETDATE()**         | **创建时间**           |
| **is_visible**      | **BIT**          | **DEFAULT 1**                 | **可见性控制**         |

**索引设计：**
- `idx_problem_contest` - 比赛ID索引
- `idx_problem_difficulty` - 难度索引

---

### **提交表 (SUBMISSION) - 记录用户代码提交和评测结果**

| **字段名**               | **数据类型**    | **约束**                                      | **说明**                   |
| ------------------------ | --------------- | --------------------------------------------- | -------------------------- |
| **submission_id**        | **BIGINT**      | **PRIMARY KEY, IDENTITY(1,1)**               | **提交唯一标识**           |
| **user_id**              | **BIGINT**      | **FOREIGN KEY, NOT NULL**                    | **用户ID**                 |
| **problem_id**           | **VARCHAR(50)** | **FOREIGN KEY, NOT NULL**                    | **题目ID**                 |
| **contest_id**           | **BIGINT**      | **FOREIGN KEY**                              | **比赛ID**                 |
| **programming_language** | **VARCHAR(50)** | **NOT NULL**                                 | **编程语言**               |
| **source_code**          | **TEXT**        | **NOT NULL**                                 | **源代码**                 |
| **source_length**        | **INT**         | **NOT NULL**                                 | **代码长度**               |
| **verdict**              | **VARCHAR(50)** | **DEFAULT 'Pending', CHECK约束**             | **评测结果**               |
| **time_consumed_ms**     | **INT**         | **DEFAULT 0**                                | **耗时（毫秒）**           |
| **memory_consumed_kb**   | **INT**         | **DEFAULT 0**                                | **内存使用（KB）**         |
| **passed_test_count**    | **INT**         | **DEFAULT 0**                                | **通过测试用例数**         |
| **test_results**         | **NVARCHAR(MAX)** | -                                          | **详细测试结果**           |
| **submission_time**      | **DATETIME2**   | **DEFAULT GETDATE()**                        | **提交时间**               |
| **relative_time**        | **INT**         | -                                            | **相对比赛时间**           |
| **points**               | **INT**         | -                                            | **得分**                   |

**索引设计：**
- `idx_submission_user_time` - 用户和时间索引
- `idx_submission_contest` - 比赛和题目索引
- `idx_submission_verdict` - 评测结果索引
- `idx_submission_problem_verdict` - 题目和评测结果索引（新增）

---

## 题目标签表 (PROBLEM_TAG) - 管理题目分类标签

| **字段名**    | **数据类型**    | **约束**                       | **说明**           |
| ------------- | --------------- | ------------------------------ | ------------------ |
| **tag_id**    | **BIGINT**      | **PRIMARY KEY, IDENTITY(1,1)** | **标签唯一标识**   |
| **name**      | **VARCHAR(50)** | **UNIQUE, NOT NULL**           | **标签名称**       |
| **description** | **TEXT**        | -                              | **标签描述**       |

**功能说明：**
- 存储题目的分类标签，如"动态规划"、"图论"、"数据结构"等
- 支持标签的唯一性约束，避免重复标签
- 通过描述字段提供标签的详细说明

**关联关系：**
- 与PROBLEM_TAG_RELATION表关联，建立题目与标签的多对多关系

---

## 测试用例表 (TEST_CASE) - 存储题目的测试数据

| **字段名**          | **数据类型**    | **约束**                       | **说明**               |
| ------------------- | --------------- | ------------------------------ | ---------------------- |
| **test_case_id**    | **BIGINT**      | **PRIMARY KEY, IDENTITY(1,1)** | **测试用例唯一标识**   |
| **problem_id**      | **VARCHAR(50)** | **FOREIGN KEY, NOT NULL**      | **所属题目ID**         |
| **input_data**      | **TEXT**        | **NOT NULL**                   | **输入数据**           |
| **expected_output** | **TEXT**        | **NOT NULL**                   | **期望输出**           |
| **is_sample**       | **BIT**         | **DEFAULT 0**                  | **是否为样例测试**     |
| **test_order**      | **INT**         | **DEFAULT 0**                  | **测试顺序**           |

**功能说明：**
- 存储每道题目的所有测试用例数据
- 支持区分样例测试和隐藏测试
- 通过test_order控制测试执行顺序
- 为代码评测提供标准输入输出对照

**索引设计：**
- `idx_test_case_problem` - 题目ID索引，快速查询某题目的所有测试用例

---

## 比赛用户关系表 (CONTEST_USER) - 记录用户参赛信息和比赛结果

| **字段名**            | **数据类型** | **约束**                                       | **说明**               |
| --------------------- | ------------ | ---------------------------------------------- | ---------------------- |
| **contest_id**        | **BIGINT**   | **PRIMARY KEY, FOREIGN KEY, NOT NULL**         | **比赛ID**             |
| **user_id**           | **BIGINT**   | **PRIMARY KEY, FOREIGN KEY, NOT NULL**         | **用户ID**             |
| **registration_time** | **DATETIME2**| **DEFAULT GETDATE()**                          | **报名时间**           |
| **role**              | **VARCHAR(30)** | **DEFAULT 'contestant', CHECK约束**          | **角色类型**           |
| **rating_before**     | **INT**      | -                                              | **赛前评分**           |
| **rating_after**      | **INT**      | -                                              | **赛后评分**           |
| **contest_rank**      | **INT**      | -                                              | **比赛排名**           |
| **solved_count**      | **INT**      | **DEFAULT 0**                                  | **解题数量**           |
| **total_penalty**     | **INT**      | **DEFAULT 0**                                  | **总罚时**             |
| **scores**            | **INT**      | **DEFAULT 0**                                  | **得分**               |

**角色类型说明：**
- `author` - 题目作者
- `tester` - 测试者
- `contestant` - 参赛者
- `out_of_competition` - 非正式参赛
- `virtual` - 虚拟参赛

**功能说明：**
- 记录用户与比赛的关联关系和参赛状态
- 存储用户在比赛中的表现和结果数据
- 支持多种角色类型，满足不同参与方式

**索引设计：**
- `idx_contest_user_role` - 角色类型索引

---

## Hack表 (HACK) - 记录Hack挑战信息

| **字段名**        | **数据类型**    | **约束**                                     | **说明**               |
| ----------------- | --------------- | -------------------------------------------- | ---------------------- |
| **hack_id**       | **BIGINT**      | **PRIMARY KEY, IDENTITY(1,1)**               | **Hack记录唯一标识**   |
| **hacker_id**     | **BIGINT**      | **FOREIGN KEY, NOT NULL**                    | **Hack发起者ID**       |
| **submission_id** | **BIGINT**      | **FOREIGN KEY, NOT NULL**                    | **被Hack的提交ID**     |
| **verdict**       | **VARCHAR(20)** | **CHECK IN ('SUCCESSFUL','UNSUCCESSFUL','INVALID')** | **Hack结果**     |
| **test_case**     | **TEXT**        | **NOT NULL**                                 | **Hack测试数据**       |
| **hack_time**     | **DATETIME2**   | **DEFAULT GETDATE()**                        | **Hack时间**           |
| **hack_result**   | **TEXT**        | -                                            | **Hack详细结果**       |

**Hack结果说明：**
- `SUCCESSFUL` - Hack成功（找到代码缺陷）
- `UNSUCCESSFUL` - Hack失败（代码正确）
- `INVALID` - Hack无效

**功能说明：**
- 记录用户之间的代码挑战行为
- 存储Hack使用的测试数据和结果
- 通过关联submission_id精确指向被挑战的提交记录
- 支持代码安全性和正确性的社区监督

**索引设计：**
- `idx_hack_time` - Hack时间索引
- `idx_hack_verdict` - Hack结果索引
- `idx_hack_submission` - 提交记录索引

## 4.3 数据完整性约束

| **约束类型** | **应用表** | **字段/关系** | **约束说明** | **实施方式** |
|------------|----------|-------------|------------|------------|
| **主键约束** | **所有表** | 主键字段 | **唯一标识每条记录** | **PRIMARY KEY** |
| **外键约束** | **CONTEST** | created_by | **创建者必须存在于用户表** | **FOREIGN KEY REFERENCES Users(user_id)** |
| **外键约束** | **PROBLEM** | contest_id | **题目所属比赛必须存在** | **FOREIGN KEY REFERENCES CONTEST(contest_id)** |
| **外键约束** | **PROBLEM_TAG_RELATION** | problem_id, tag_id | **标签关系必须引用有效题目和标签** | **FOREIGN KEY REFERENCES PROBLEM(problem_id), PROBLEM_TAG(tag_id)** |
| **外键约束** | **TEST_CASE** | problem_id | **测试用例必须属于有效题目** | **FOREIGN KEY REFERENCES PROBLEM(problem_id) ON DELETE CASCADE** |
| **外键约束** | **SUBMISSION** | user_id, problem_id, contest_id | **提交记录必须关联有效用户、题目和比赛** | **FOREIGN KEY REFERENCES Users(user_id), PROBLEM(problem_id), CONTEST(contest_id)** |
| **外键约束** | **CONTEST_USER** | contest_id, user_id | **参赛记录必须关联有效比赛和用户** | **FOREIGN KEY REFERENCES CONTEST(contest_id), Users(user_id) ON DELETE CASCADE** |
| **外键约束** | **HACK** | hacker_id, submission_id | **Hack记录必须关联有效用户和提交** | **FOREIGN KEY REFERENCES Users(user_id), SUBMISSION(submission_id) ON DELETE CASCADE** |
| **唯一约束** | **Users** | handle | **用户名唯一** | **UNIQUE NOT NULL** |
| **唯一约束** | **Users** | email | **邮箱地址唯一** | **UNIQUE NOT NULL** |
| **唯一约束** | **PROBLEM_TAG** | name | **标签名称唯一** | **UNIQUE NOT NULL** |
| **唯一约束** | **PROBLEM_TAG_RELATION** | problem_id, tag_id | **题目标签组合唯一** | **PRIMARY KEY (复合主键)** |
| **唯一约束** | **CONTEST_USER** | contest_id, user_id | **用户参赛记录唯一** | **PRIMARY KEY (复合主键)** |
| **检查约束** | **CONTEST** | type | **比赛类型枚举值控制** | **CHECK (type IN ('CF', 'IOI', 'ICPC'))** |
| **检查约束** | **CONTEST** | phase | **比赛阶段状态控制** | **CHECK (phase IN ('BEFORE', 'CODING', 'PENDING_SYSTEM_TEST', 'SYSTEM_TEST', 'FINISHED'))** |
| **检查约束** | **SUBMISSION** | verdict | **判题结果状态控制** | **CHECK (verdict IN ('Pending', 'Running', 'Accepted', 'Wrong Answer', 'Time Limit Exceeded', 'Memory Limit Exceeded', 'Runtime Error', 'Compilation Error', 'Presentation Error', 'Failed', 'Idleness Limit Exceeded', 'Partial Solution', 'Skipped', 'Challenged', 'Rejected'))** |
| **检查约束** | **CONTEST_USER** | role | **参赛角色类型控制** | **CHECK (role IN ('author', 'tester', 'contestant', 'out_of_competition', 'virtual'))** |
| **检查约束** | **HACK** | verdict | **Hack结果状态控制** | **CHECK (verdict IN ('SUCCESSFUL', 'UNSUCCESSFUL', 'INVALID'))** |
| **检查约束** | **Users** | rating, max_rating | **评分非负约束** | **CHECK (rating >= 0 AND max_rating >= 0)** |
| **检查约束** | **CONTEST** | duration_seconds | **比赛时长正数约束** | **CHECK (duration_seconds > 0)** |
| **检查约束** | **PROBLEM** | time_limit_ms, memory_limit_kb | **题目限制正数约束** | **CHECK (time_limit_ms > 0 AND memory_limit_kb > 0)** |
| **检查约束** | **SUBMISSION** | time_consumed_ms, memory_consumed_kb | **资源消耗非负约束** | **CHECK (time_consumed_ms >= 0 AND memory_consumed_kb >= 0)** |
| **默认约束** | **Users** | rating, max_rating | **默认评分0** | **DEFAULT 0** |
| **默认约束** | **Users** | user_rank, max_rank | **默认等级'Newbie'** | **DEFAULT 'Newbie'** |
| **默认约束** | **Users** | registration_time, last_online_time | **默认当前时间** | **DEFAULT GETDATE()** |
| **默认约束** | **Users** | is_admin, is_active | **默认权限和状态** | **DEFAULT 0, DEFAULT 1** |
| **默认约束** | **CONTEST** | type, phase, frozen | **默认比赛属性** | **DEFAULT 'CF', DEFAULT 'BEFORE', DEFAULT 0** |
| **默认约束** | **PROBLEM** | time_limit_ms, memory_limit_kb, is_visible | **默认题目属性** | **DEFAULT 1000, DEFAULT 256000, DEFAULT 1** |
| **默认约束** | **SUBMISSION** | verdict, submission_time | **默认提交状态和时间** | **DEFAULT 'Pending', DEFAULT GETDATE()** |
| **默认约束** | **TEST_CASE** | is_sample | **默认非样例测试** | **DEFAULT 0** |
| **非空约束** | **Users** | handle, email, password | **用户关键信息必填** | **NOT NULL** |
| **非空约束** | **CONTEST** | name, start_time, duration_seconds | **比赛关键信息必填** | **NOT NULL** |
| **非空约束** | **PROBLEM** | problem_id, title | **题目关键信息必填** | **NOT NULL** |
| **非空约束** | **PROBLEM_TAG** | name | **标签名称必填** | **NOT NULL** |
| **非空约束** | **SUBMISSION** | user_id, problem_id, programming_language, source_code | **提交关键信息必填** | **NOT NULL** |
| **非空约束** | **TEST_CASE** | problem_id, input_data, expected_output | **测试用例数据必填** | **NOT NULL** |
| **非空约束** | **HACK** | hacker_id, submission_id, verdict, test_case | **Hack关键信息必填** | **NOT NULL** |

### 4.4 性能优化

| **优化方面** | **实施策略**                                       | **预期效果**                   |
| ------------ | -------------------------------------------------- | ------------------------------ |
| **索引策略** | **为常用查询字段创建索引，复合索引优化多条件查询** | **提高查询速度，减少全表扫描** |
| **查询优化** | **使用参数化查询，避免全表扫描，合理使用连接查询** | **提升系统响应性能**           |
| **缓存机制** | **热点数据缓存，查询结果缓存**                     | **减少数据库访问压力**         |
| **定期维护** | **索引统计信息更新，数据碎片整理**                 | **保持数据库性能稳定**         |

## 5. 数据查询功能

### 5.1 用户信息查询
**支持查询所有用户的公开信息，包括：**
- **基础身份信息：用户ID、用户名（handle）、邮箱**
- **评分相关信息：当前评分、最高评分、当前等级、最高等级**
- **个人资料信息：国家、城市、组织、头像**
- **活跃度信息：注册时间、最后在线时间、贡献值**
- **权限标识：是否为管理员、账号活跃状态**

### 5.2 比赛信息查询
**支持查询所有比赛的详细信息，包括：**
- **基本信息：比赛ID、名称、类型（CF/IOI/ICPC）**
- **时间信息：开始时间、持续时间（秒）**
- **描述信息：官方网址、比赛描述、难度评级、比赛类型、ICPC区域等**
- **归属信息：比赛创建者**

### 5.3 题目信息查询
**支持查询所有题目的完整信息，包括：**
- **标识信息：题目ID（唯一）、所属比赛、题目索引（如A、B、C）**
- **题目内容：标题、题目描述、输入输出规范、样例数据**
- **限制条件：时间限制、内存限制**
- **统计数据：通过数、总提交数、难度评级**

### 5.4 提交记录查询
**支持查询所有代码提交记录的详细信息，包括：**
- **基本标识：提交ID、用户ID、题目ID、比赛ID**
- **代码信息：编程语言、源代码内容、代码长度**
- **评测结果：状态（AC/WRONG_ANSWER等）、运行耗时、内存使用量**
- **测试详情：通过测试用例数、详细测试结果、提交时间**
- **Hack相关：是否被Hack**

### 5.5 比赛排名查询
**支持查询特定比赛的排名情况，包括：**
- **用户角色：参赛者或虚拟参赛（VP）**
- **评分变化：比赛前后的用户评分变化**
- **排名详情：比赛排名、解题数量、罚分、最终得分**

### 5.6 查询高级功能
**所有查询功能均支持对数据列的筛选功能，可根据需要选择显示特定字段。**

## 6. 数据修改功能

### 6.1 用户注册
**实现新用户账号注册功能：**
- **在用户表中添加新用户的完整信息**
- **用户名和邮箱唯一性验证**
- **密码强度校验和加密存储**
- **初始化用户统计信息和权限设置**

### 6.2 题目与比赛创建
**支持创建新题目和新比赛：**
- **在题目表中添加新题目的详细信息**
- **在比赛表中添加新比赛的完整信息**
- **设置题目与比赛的关联关系**
- **配置测试用例和评测参数**

### 6.3 代码提交
**支持用户提交代码进行评测：**
- **在提交表中添加提交记录信息**
- **代码语法和安全性检查**
- **自动分配评测任务**
- **实时更新评测状态和结果**

---
**文档版本：v2.1**  
**更新日期：2024年1月**  
**负责人：数据库设计团队**