-- 创建数据库
CREATE DATABASE OJ;
GO

USE OJ;
GO

-- 用户表
CREATE TABLE Users (
    user_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    handle VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    rating INT DEFAULT 0,
    max_rating INT DEFAULT 0,
    user_rank VARCHAR(50) DEFAULT 'Newbie',
    max_rank VARCHAR(50) DEFAULT 'Newbie',
    country VARCHAR(100),
    city VARCHAR(100),
    organization VARCHAR(200),
    avatar VARCHAR(500),
    registration_time DATETIME2 DEFAULT GETDATE(),
    last_online_time DATETIME2 DEFAULT GETDATE(),
    contribution INT DEFAULT 0,
    is_admin BIT DEFAULT 0,
    is_active BIT DEFAULT 1
);
GO

-- 创建用户表索引
CREATE INDEX idx_user_rating ON Users(rating);
CREATE INDEX idx_user_handle ON Users(handle);
CREATE INDEX idx_user_rank ON Users(user_rank);
GO

-- 比赛表
CREATE TABLE CONTEST (
    contest_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(10) NOT NULL DEFAULT 'CF' CHECK (type IN ('CF', 'IOI', 'ICPC')),
    phase VARCHAR(30) DEFAULT 'BEFORE' CHECK (phase IN ('BEFORE', 'CODING', 'PENDING_SYSTEM_TEST', 'SYSTEM_TEST', 'FINISHED')),
    frozen BIT DEFAULT 0,
    start_time DATETIME2 NOT NULL,
    duration_seconds INT NOT NULL,
    website_url VARCHAR(500),
    description TEXT,
    difficulty INT DEFAULT 0,
    kind VARCHAR(100),
    icpc_region VARCHAR(100),
    country VARCHAR(100),
    city VARCHAR(100),
    season VARCHAR(50),
    created_by BIGINT,
    FOREIGN KEY (created_by) REFERENCES Users (user_id)
);
GO

-- 创建比赛表索引
CREATE INDEX idx_contest_time ON CONTEST(start_time);
CREATE INDEX idx_contest_type ON CONTEST(type);
GO

-- 题目表
CREATE TABLE PROBLEM (
    problem_id VARCHAR(50) PRIMARY KEY,
    contest_id BIGINT,
    problem_index VARCHAR(10),
    title VARCHAR(300) NOT NULL,
    statement TEXT,
    input_specification TEXT,
    output_specification TEXT,
    sample_tests NVARCHAR(MAX),
    notes TEXT,
    time_limit_ms INT NOT NULL DEFAULT 1000,
    memory_limit_kb INT NOT NULL DEFAULT 256000,
    difficulty VARCHAR(10),
    accepted_count INT DEFAULT 0,
    submission_count INT DEFAULT 0,
    creation_time DATETIME2 DEFAULT GETDATE(),
    is_visible BIT DEFAULT 1,
    FOREIGN KEY (contest_id) REFERENCES CONTEST(contest_id)
);
GO

-- 创建题目表索引
CREATE INDEX idx_problem_contest ON PROBLEM(contest_id);
CREATE INDEX idx_problem_difficulty ON PROBLEM(difficulty);
GO

-- 题目标签表
CREATE TABLE PROBLEM_TAG (
    tag_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);
GO

-- 题目标签关系表
CREATE TABLE PROBLEM_TAG_RELATION (
    problem_id VARCHAR(50) NOT NULL,
    tag_id BIGINT NOT NULL,
    PRIMARY KEY (problem_id, tag_id),
    FOREIGN KEY (problem_id) REFERENCES PROBLEM(problem_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES PROBLEM_TAG(tag_id) ON DELETE CASCADE
);
GO

-- 测试用例表
CREATE TABLE TEST_CASE (
    test_case_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    problem_id VARCHAR(50) NOT NULL,
    input_data TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    is_sample BIT DEFAULT 0,
    test_order INT DEFAULT 0,
    FOREIGN KEY (problem_id) REFERENCES PROBLEM(problem_id) ON DELETE CASCADE
);
GO

-- 创建测试用例表索引
CREATE INDEX idx_test_case_problem ON TEST_CASE(problem_id);
GO

-- 提交表
CREATE TABLE SUBMISSION (
    submission_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    problem_id VARCHAR(50) NOT NULL,
    contest_id BIGINT,
    programming_language VARCHAR(50) NOT NULL,
    source_code TEXT NOT NULL,
    source_length INT NOT NULL,
    verdict VARCHAR(30) DEFAULT 'PENDING' CHECK (verdict IN (
        'PENDING', 'RUNNING', 'ACCEPTED', 'WRONG_ANSWER', 'TIME_LIMIT_EXCEEDED',
        'MEMORY_LIMIT_EXCEEDED', 'RUNTIME_ERROR', 'COMPILATION_ERROR',
        'PRESENTATION_ERROR', 'FAILED'
    )),
    time_consumed_ms INT DEFAULT 0,
    memory_consumed_kb INT DEFAULT 0,
    passed_test_count INT DEFAULT 0,
    test_results NVARCHAR(MAX),
    submission_time DATETIME2 DEFAULT GETDATE(),
    relative_time INT,
    points INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (problem_id) REFERENCES PROBLEM(problem_id),
    FOREIGN KEY (contest_id) REFERENCES CONTEST(contest_id)
);
GO

-- 创建提交表索引
CREATE INDEX idx_submission_user_time ON SUBMISSION(user_id, submission_time);
CREATE INDEX idx_submission_contest ON SUBMISSION(contest_id, problem_id);
CREATE INDEX idx_submission_verdict ON SUBMISSION(verdict);
GO

-- 比赛用户关系表
CREATE TABLE CONTEST_USER (
    contest_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    registration_time DATETIME2 DEFAULT GETDATE(),
    role VARCHAR(30) NOT NULL DEFAULT 'contestant' CHECK (role IN ('author', 'tester', 'contestant', 'out_of_competition', 'virtual')),
    rating_before INT,
    rating_after INT,
    contest_rank INT,
    solved_count INT DEFAULT 0,
    total_penalty INT DEFAULT 0,
    scores INT DEFAULT 0,
    PRIMARY KEY (contest_id, user_id),
    FOREIGN KEY (contest_id) REFERENCES CONTEST(contest_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);
GO

-- 创建比赛用户关系表索引
CREATE INDEX idx_contest_user_role ON CONTEST_USER(role);
GO

-- Hack表
CREATE TABLE HACK (
    hack_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    hacker_id BIGINT NOT NULL,
    defender_id BIGINT NOT NULL,
    problem_id VARCHAR(50) NOT NULL,
    contest_id BIGINT NOT NULL,
    verdict VARCHAR(20) NOT NULL CHECK (verdict IN ('SUCCESSFUL', 'UNSUCCESSFUL', 'INVALID')),
    test_case TEXT NOT NULL,
    hack_time DATETIME2 DEFAULT GETDATE(),
    hack_result TEXT,
    FOREIGN KEY (hacker_id) REFERENCES Users(user_id),
    FOREIGN KEY (defender_id) REFERENCES Users(user_id),
    FOREIGN KEY (problem_id) REFERENCES PROBLEM(problem_id),
    FOREIGN KEY (contest_id) REFERENCES CONTEST(contest_id)
);
GO

-- 创建Hack表索引
CREATE INDEX idx_hack_time ON HACK(hack_time);
CREATE INDEX idx_hack_verdict ON HACK(verdict);
GO