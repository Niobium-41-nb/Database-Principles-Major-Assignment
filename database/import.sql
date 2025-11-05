-- import_test_data.sql
-- 为 OJ 数据库生成大量测试数据（与现有结构保持一致）

USE OJ;
GO

-- 首先清空所有表（如果已有数据）
DELETE FROM HACK;
DELETE FROM CONTEST_USER;
DELETE FROM SUBMISSION;
DELETE FROM TEST_CASE;
DELETE FROM PROBLEM_TAG_RELATION;
DELETE FROM PROBLEM_TAG;
DELETE FROM PROBLEM;
DELETE FROM CONTEST;
DELETE FROM Users;
GO

-- 重置身份列
DBCC CHECKIDENT ('Users', RESEED, 0);
DBCC CHECKIDENT ('CONTEST', RESEED, 0);
DBCC CHECKIDENT ('PROBLEM_TAG', RESEED, 0);
DBCC CHECKIDENT ('TEST_CASE', RESEED, 0);
DBCC CHECKIDENT ('SUBMISSION', RESEED, 0);
DBCC CHECKIDENT ('HACK', RESEED, 0);
GO

-- 1. 插入用户数据 (扩展版本)
INSERT INTO Users (handle, email, password, name, rating, max_rating, user_rank, max_rank, country, city, organization, avatar, contribution, is_admin)
VALUES 
('tourist', 'tourist@example.com', 'hashed_password_1', 'Gennady Korotkevich', 3500, 3850, 'Legendary Grandmaster', 'Legendary Grandmaster', 'Belarus', 'Gomel', 'ITMO University', 'avatar1.jpg', 150, 0),
('petr', 'petr@example.com', 'hashed_password_2', 'Petr Mitrichev', 3200, 3700, 'International Grandmaster', 'International Grandmaster', 'Russia', 'Moscow', 'Google', 'avatar2.jpg', 200, 0),
('alice', 'alice@example.com', 'hashed_password_3', 'Alice Smith', 1600, 1800, 'Expert', 'Expert', 'USA', 'New York', 'MIT', 'avatar3.jpg', 50, 0),
('bob', 'bob@example.com', 'hashed_password_4', 'Bob Johnson', 1200, 1300, 'Pupil', 'Specialist', 'UK', 'London', 'Cambridge', 'avatar4.jpg', 10, 0),
('admin_user', 'admin@example.com', 'hashed_admin_password', 'System Admin', 0, 0, 'Newbie', 'Newbie', 'International', 'Virtual', 'Codeforces', 'admin.jpg', 500, 1),
('um_nik', 'umnik@example.com', 'hashed_password_5', 'Nikolay Kalinin', 3300, 3450, 'International Grandmaster', 'International Grandmaster', 'Russia', 'St. Petersburg', 'ITMO University', 'avatar5.jpg', 80, 0),
('errichto', 'errichto@example.com', 'hashed_password_6', 'Kamil Dębowski', 3000, 3200, 'Grandmaster', 'Grandmaster', 'Poland', 'Warsaw', 'Google', 'avatar6.jpg', 120, 0),
('benq', 'benq@example.com', 'hashed_password_7', 'Benjamin Qi', 3400, 3600, 'International Grandmaster', 'International Grandmaster', 'USA', 'New York', 'MIT', 'avatar7.jpg', 90, 0);
GO

-- 2. 插入比赛数据 (扩展版本)
INSERT INTO CONTEST (name, type, phase, start_time, duration_seconds, website_url, description, difficulty, kind, icpc_region, country, city, season, created_by)
VALUES 
('Codeforces Round #1000 (Div. 1)', 'CF', 'FINISHED', '2024-01-15 14:00:00', 7200, 'https://codeforces.com/contest/1000', 'Celebratory Round #1000', 5, 'CF Round', 'Europe', 'Russia', 'Moscow', 'Winter 2024', (SELECT user_id FROM Users WHERE handle = 'admin_user')),
('ICPC World Finals 2024', 'ICPC', 'FINISHED', '2024-03-20 09:00:00', 18000, 'https://icpc.global/finals', 'ICPC World Finals', 5, 'ICPC Finals', 'Global', 'Egypt', 'Sharm El-Sheikh', '2024', (SELECT user_id FROM Users WHERE handle = 'admin_user')),
('Educational Codeforces Round 200', 'CF', 'FINISHED', '2024-02-10 17:00:00', 7200, 'https://codeforces.com/contest/200', 'Educational Round', 3, 'Educational', 'Global', 'Virtual', 'Online', 'Winter 2024', (SELECT user_id FROM Users WHERE handle = 'admin_user')),
('Weekly Contest 350', 'CF', 'FINISHED', '2024-04-15 12:00:00', 7200, 'https://codeforces.com/contest/350', 'Weekly Contest', 2, 'CF Round', 'Global', 'Virtual', 'Online', 'Spring 2024', (SELECT user_id FROM Users WHERE handle = 'admin_user')),
('Google Code Jam 2024 Round 1', 'IOI', 'FINISHED', '2024-05-01 10:00:00', 15000, 'https://codingcompetitions.withgoogle.com/codejam', 'Google Code Jam Round 1', 4, 'Code Jam', 'Global', 'Virtual', 'Online', '2024', (SELECT user_id FROM Users WHERE handle = 'admin_user'));
GO

-- 3. 插入题目标签数据 (扩展版本)
INSERT INTO PROBLEM_TAG (name, description)
VALUES 
('math', 'Problems involving mathematical concepts and calculations'),
('greedy', 'Problems that can be solved using greedy algorithms'),
('dp', 'Dynamic programming problems'),
('graphs', 'Problems related to graph theory'),
('implementation', 'Problems that require careful implementation'),
('brute force', 'Problems solvable by trying all possibilities'),
('data structures', 'Problems involving advanced data structures'),
('binary search', 'Problems solved using binary search techniques'),
('geometry', 'Computational geometry problems'),
('strings', 'String manipulation and algorithms'),
('bitmasks', 'Bit manipulation problems'),
('combinatorics', 'Combinatorial mathematics problems');
GO

-- 4. 插入题目数据 (扩展版本) - 移除了accepted_count和submission_count字段
DECLARE @contest1_id BIGINT, @contest2_id BIGINT, @contest3_id BIGINT, @contest4_id BIGINT, @contest5_id BIGINT;
SELECT @contest1_id = contest_id FROM CONTEST WHERE name = 'Codeforces Round #1000 (Div. 1)';
SELECT @contest2_id = contest_id FROM CONTEST WHERE name = 'ICPC World Finals 2024';
SELECT @contest3_id = contest_id FROM CONTEST WHERE name = 'Educational Codeforces Round 200';
SELECT @contest4_id = contest_id FROM CONTEST WHERE name = 'Weekly Contest 350';
SELECT @contest5_id = contest_id FROM CONTEST WHERE name = 'Google Code Jam 2024 Round 1';

INSERT INTO PROBLEM (problem_id, contest_id, problem_index, title, statement, input_specification, output_specification, sample_tests, time_limit_ms, memory_limit_kb, difficulty)
VALUES 
('CF1000A', @contest1_id, 'A', 'Watermelon', 'One hot summer day Pete and his friend Billy decided to buy a watermelon...', 'The first (and the only) input line contains integer number w (1 ≤ w ≤ 100)...', 'Print YES, if the boys can divide the watermelon into two parts...', '[{"input": "8", "output": "YES"}, {"input": "5", "output": "NO"}]', 1000, 256000, '800'),
('CF1000B', @contest1_id, 'B', 'Prime Subtraction', 'You are given two integers x and y. You can perform multiple operations...', 'The first line contains a single integer t (1 ≤ t ≤ 1000) — the number of test cases...', 'For each test case, print "YES" if you can make x equal to y...', '[{"input": "4\n100 98\n42 32\n100 100\n100 97", "output": "YES\nYES\nYES\nNO"}]', 2000, 512000, '1200'),
('CF1000C', @contest1_id, 'C', 'Complex Problem', 'This is a more complex problem for the contest...', 'Input format description...', 'Output format description...', '[{"input": "1\n2", "output": "3"}]', 3000, 1048576, '1800'),
('CF1000D', @contest1_id, 'D', 'Dynamic Programming', 'A dynamic programming problem of medium difficulty...', 'Input specification for DP problem...', 'Output specification for DP problem...', '[{"input": "5\n1 2 3 4 5", "output": "15"}]', 2000, 512000, '2000'),
('EDU200A', @contest3_id, 'A', 'Educational Problem A', 'Educational problem statement...', 'Educational input specification...', 'Educational output specification...', '[{"input": "test", "output": "result"}]', 1500, 256000, '1000'),
('EDU200B', @contest3_id, 'B', 'Educational Problem B', 'Another educational problem...', 'Input for educational problem B...', 'Output for educational problem B...', '[{"input": "3 4", "output": "7"}]', 1500, 256000, '1300'),
('WEEK350A', @contest4_id, 'A', 'Weekly Problem A', 'Weekly contest problem A...', 'Input specification...', 'Output specification...', '[{"input": "1", "output": "2"}]', 1000, 256000, '900'),
('GCJ2024R1A', @contest5_id, 'A', 'Code Jam Problem A', 'Google Code Jam problem statement...', 'Code Jam input format...', 'Code Jam output format...', '[{"input": "Case #1: test", "output": "Case #1: result"}]', 3000, 1048576, '1500');
GO

-- 5. 插入题目标签关系数据 (扩展版本)
INSERT INTO PROBLEM_TAG_RELATION (problem_id, tag_id)
SELECT p.problem_id, pt.tag_id
FROM PROBLEM p
CROSS APPLY (
    VALUES 
    ('CF1000A', 'math'), ('CF1000A', 'implementation'),
    ('CF1000B', 'math'), ('CF1000B', 'greedy'),
    ('CF1000C', 'dp'), ('CF1000C', 'graphs'),
    ('CF1000D', 'dp'), ('CF1000D', 'combinatorics'),
    ('EDU200A', 'implementation'), ('EDU200A', 'brute force'),
    ('EDU200B', 'math'), ('EDU200B', 'binary search'),
    ('WEEK350A', 'greedy'), ('WEEK350A', 'implementation'),
    ('GCJ2024R1A', 'data structures'), ('GCJ2024R1A', 'strings')
) AS v(pid, tag_name)
JOIN PROBLEM_TAG pt ON pt.name = v.tag_name
WHERE p.problem_id = v.pid;
GO

-- 6. 插入测试用例数据 (扩展版本)
INSERT INTO TEST_CASE (problem_id, input_data, expected_output, is_sample, test_order)
VALUES 
('CF1000A', '8', 'YES', 1, 1),
('CF1000A', '5', 'NO', 1, 2),
('CF1000A', '10', 'YES', 0, 3),
('CF1000A', '3', 'NO', 0, 4),
('CF1000A', '100', 'YES', 0, 5),
('CF1000B', '4', 'YES', 1, 1),
('CF1000B', '100 98', 'YES', 0, 2),
('CF1000B', '42 32', 'YES', 0, 3),
('CF1000B', '100 97', 'NO', 0, 4),
('CF1000C', '1', '3', 1, 1),
('CF1000C', '5', '15', 0, 2),
('CF1000D', '5\n1 2 3 4 5', '15', 1, 1),
('EDU200A', 'test', 'result', 1, 1),
('EDU200B', '3 4', '7', 1, 1),
('WEEK350A', '1', '2', 1, 1),
('GCJ2024R1A', 'Case #1: test', 'Case #1: result', 1, 1);
GO

-- 7. 插入比赛用户关系数据 (扩展版本)
DECLARE @contest1_id BIGINT, @contest3_id BIGINT, @contest4_id BIGINT, @contest5_id BIGINT;
SELECT @contest1_id = contest_id FROM CONTEST WHERE name = 'Codeforces Round #1000 (Div. 1)';
SELECT @contest3_id = contest_id FROM CONTEST WHERE name = 'Educational Codeforces Round 200';
SELECT @contest4_id = contest_id FROM CONTEST WHERE name = 'Weekly Contest 350';
SELECT @contest5_id = contest_id FROM CONTEST WHERE name = 'Google Code Jam 2024 Round 1';

INSERT INTO CONTEST_USER (contest_id, user_id, role, rating_before, rating_after, contest_rank, solved_count, total_penalty, scores)
VALUES 
(@contest1_id, (SELECT user_id FROM Users WHERE handle = 'tourist'), 'contestant', 3480, 3500, 1, 5, 120, 4500),
(@contest1_id, (SELECT user_id FROM Users WHERE handle = 'petr'), 'contestant', 3180, 3200, 2, 4, 180, 4200),
(@contest1_id, (SELECT user_id FROM Users WHERE handle = 'um_nik'), 'contestant', 3280, 3300, 3, 4, 200, 4100),
(@contest1_id, (SELECT user_id FROM Users WHERE handle = 'errichto'), 'contestant', 2980, 3000, 4, 3, 250, 3800),
(@contest1_id, (SELECT user_id FROM Users WHERE handle = 'benq'), 'contestant', 3380, 3400, 5, 3, 280, 3700),
(@contest1_id, (SELECT user_id FROM Users WHERE handle = 'alice'), 'contestant', 1580, 1600, 150, 2, 450, 1800),
(@contest1_id, (SELECT user_id FROM Users WHERE handle = 'bob'), 'contestant', 1180, 1200, 300, 1, 600, 800),

(@contest3_id, (SELECT user_id FROM Users WHERE handle = 'alice'), 'contestant', 1550, 1600, 50, 3, 200, 2200),
(@contest3_id, (SELECT user_id FROM Users WHERE handle = 'bob'), 'contestant', 1150, 1200, 120, 2, 350, 1500),

(@contest4_id, (SELECT user_id FROM Users WHERE handle = 'alice'), 'contestant', 1580, 1620, 25, 4, 180, 2400),
(@contest4_id, (SELECT user_id FROM Users WHERE handle = 'bob'), 'contestant', 1180, 1220, 80, 3, 280, 1900),
(@contest4_id, (SELECT user_id FROM Users WHERE handle = 'errichto'), 'contestant', 2950, 3000, 1, 5, 100, 4200),

(@contest5_id, (SELECT user_id FROM Users WHERE handle = 'tourist'), 'contestant', 3450, 3500, 1, 3, 150, 100),
(@contest5_id, (SELECT user_id FROM Users WHERE handle = 'petr'), 'contestant', 3150, 3200, 2, 3, 180, 90),
(@contest5_id, (SELECT user_id FROM Users WHERE handle = 'benq'), 'contestant', 3350, 3400, 3, 2, 200, 80);
GO

-- 8. 插入提交数据 (扩展版本，使用一致的评测结果格式)
DECLARE @contest1_id BIGINT, @contest3_id BIGINT, @contest4_id BIGINT, @contest5_id BIGINT;
SELECT @contest1_id = contest_id FROM CONTEST WHERE name = 'Codeforces Round #1000 (Div. 1)';
SELECT @contest3_id = contest_id FROM CONTEST WHERE name = 'Educational Codeforces Round 200';
SELECT @contest4_id = contest_id FROM CONTEST WHERE name = 'Weekly Contest 350';
SELECT @contest5_id = contest_id FROM CONTEST WHERE name = 'Google Code Jam 2024 Round 1';

INSERT INTO SUBMISSION (user_id, problem_id, contest_id, programming_language, source_code, source_length, verdict, time_consumed_ms, memory_consumed_kb, passed_test_count, submission_time, points)
VALUES 
-- CF1000A 提交
((SELECT user_id FROM Users WHERE handle = 'tourist'), 'CF1000A', @contest1_id, 'GNU C++17', '#include <iostream>
using namespace std;
int main() { int w; cin >> w; cout << (w % 2 == 0 && w > 2 ? "YES" : "NO"); return 0; }', 98, 'Accepted', 15, 4000, 4, '2024-01-15 14:05:00', 100),

((SELECT user_id FROM Users WHERE handle = 'petr'), 'CF1000A', @contest1_id, 'Java 11', 'import java.util.*; public class Main { public static void main(String[] args) { Scanner sc = new Scanner(System.in); int w = sc.nextInt(); System.out.println(w % 2 == 0 && w > 2 ? "YES" : "NO"); } }', 150, 'Accepted', 78, 16384, 4, '2024-01-15 14:06:00', 100),

((SELECT user_id FROM Users WHERE handle = 'alice'), 'CF1000A', @contest1_id, 'Python 3', 'w = int(input())
print("YES" if w % 2 == 0 and w > 2 else "NO")', 56, 'Wrong Answer', 30, 8192, 2, '2024-01-15 14:07:00', 0),

((SELECT user_id FROM Users WHERE handle = 'bob'), 'CF1000A', @contest1_id, 'C++', '#include <iostream>
int main() { int w; std::cin >> w; if (w == 2) std::cout << "YES"; else std::cout << "NO"; }', 85, 'Time Limit Exceeded', 2000, 512000, 0, '2024-01-15 14:08:00', 0),

-- CF1000B 提交
((SELECT user_id FROM Users WHERE handle = 'alice'), 'CF1000B', @contest1_id, 'Python 3', 'print("YES")', 12, 'Runtime Error', 45, 16384, 0, '2024-01-15 14:10:00', 0),

((SELECT user_id FROM Users WHERE handle = 'bob'), 'CF1000C', @contest1_id, 'Java', 'public class Main { public static void main(String[] args) { } }', 55, 'Compilation Error', 0, 0, 0, '2024-01-15 14:12:00', 0),

((SELECT user_id FROM Users WHERE handle = 'petr'), 'CF1000B', @contest1_id, 'C++', '#include <bits/stdc++.h>
using namespace std;', 35, 'Memory Limit Exceeded', 1500, 262144, 3, '2024-01-15 14:15:00', 50),

-- 其他比赛的提交
((SELECT user_id FROM Users WHERE handle = 'errichto'), 'EDU200A', @contest3_id, 'C++', '#include <iostream>
using namespace std;
int main() { cout << "result" << endl; return 0; }', 65, 'Accepted', 20, 4096, 1, '2024-02-10 17:05:00', 100),

((SELECT user_id FROM Users WHERE handle = 'um_nik'), 'WEEK350A', @contest4_id, 'GNU C++17', '#include <bits/stdc++.h>
using namespace std;
int main() { int n; cin >> n; cout << n + 1 << endl; }', 75, 'Accepted', 25, 4096, 1, '2024-04-15 12:10:00', 100),

((SELECT user_id FROM Users WHERE handle = 'benq'), 'GCJ2024R1A', @contest5_id, 'Python 3', 'print("Case #1: result")', 25, 'Accepted', 100, 8192, 1, '2024-05-01 10:30:00', 100);
GO

-- 修改Hack数据插入部分
DELETE FROM HACK;
GO

DBCC CHECKIDENT ('HACK', RESEED, 0);
GO

-- 插入Hack数据 (使用新的表结构)
DECLARE @submission1_id BIGINT, @submission2_id BIGINT, @submission3_id BIGINT, @submission4_id BIGINT;
SELECT @submission1_id = submission_id FROM SUBMISSION WHERE user_id = (SELECT user_id FROM Users WHERE handle = 'alice') AND problem_id = 'CF1000A';
SELECT @submission2_id = submission_id FROM SUBMISSION WHERE user_id = (SELECT user_id FROM Users WHERE handle = 'bob') AND problem_id = 'CF1000A';
SELECT @submission3_id = submission_id FROM SUBMISSION WHERE user_id = (SELECT user_id FROM Users WHERE handle = 'alice') AND problem_id = 'CF1000B';
SELECT @submission4_id = submission_id FROM SUBMISSION WHERE user_id = (SELECT user_id FROM Users WHERE handle = 'bob') AND problem_id = 'CF1000A' AND verdict = 'Time Limit Exceeded';

INSERT INTO HACK (hacker_id, submission_id, verdict, test_case, hack_result)
VALUES 
((SELECT user_id FROM Users WHERE handle = 'tourist'), @submission1_id, 'SUCCESSFUL', '{"input": "7"}', 'Expected: NO, Received: YES'),
((SELECT user_id FROM Users WHERE handle = 'petr'), @submission2_id, 'UNSUCCESSFUL', '{"input": "2"}', 'Expected: NO, Received: NO - Hack failed'),
((SELECT user_id FROM Users WHERE handle = 'um_nik'), @submission3_id, 'SUCCESSFUL', '{"input": "1 1"}', 'Expected: YES, Received: NO'),
((SELECT user_id FROM Users WHERE handle = 'errichto'), @submission4_id, 'INVALID', '{"input": "0"}', 'Invalid test case - number out of range');
GO

-- 验证数据插入
SELECT 'Users: ' + CAST(COUNT(*) AS VARCHAR) FROM Users
UNION ALL
SELECT 'Contests: ' + CAST(COUNT(*) AS VARCHAR) FROM CONTEST
UNION ALL
SELECT 'Problems: ' + CAST(COUNT(*) AS VARCHAR) FROM PROBLEM
UNION ALL
SELECT 'Tags: ' + CAST(COUNT(*) AS VARCHAR) FROM PROBLEM_TAG
UNION ALL
SELECT 'Tag Relations: ' + CAST(COUNT(*) AS VARCHAR) FROM PROBLEM_TAG_RELATION
UNION ALL
SELECT 'Test Cases: ' + CAST(COUNT(*) AS VARCHAR) FROM TEST_CASE
UNION ALL
SELECT 'Submissions: ' + CAST(COUNT(*) AS VARCHAR) FROM SUBMISSION
UNION ALL
SELECT 'Contest Users: ' + CAST(COUNT(*) AS VARCHAR) FROM CONTEST_USER
UNION ALL
SELECT 'Hacks: ' + CAST(COUNT(*) AS VARCHAR) FROM HACK;
GO

PRINT '扩展测试数据导入完成！';