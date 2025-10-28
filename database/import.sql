-- 使用数据库
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

-- 1. 插入用户数据
INSERT INTO Users (handle, email, password, name, rating, max_rating, user_rank, max_rank, country, city, organization, avatar, contribution, is_admin)
VALUES 
('tourist', 'tourist@example.com', 'hashed_password_1', 'Gennady Korotkevich', 3500, 3850, 'Legendary Grandmaster', 'Legendary Grandmaster', 'Belarus', 'Gomel', 'ITMO University', 'avatar1.jpg', 150, 0),
('petr', 'petr@example.com', 'hashed_password_2', 'Petr Mitrichev', 3200, 3700, 'International Grandmaster', 'International Grandmaster', 'Russia', 'Moscow', 'Google', 'avatar2.jpg', 200, 0),
('alice', 'alice@example.com', 'hashed_password_3', 'Alice Smith', 1600, 1800, 'Expert', 'Expert', 'USA', 'New York', 'MIT', 'avatar3.jpg', 50, 0),
('bob', 'bob@example.com', 'hashed_password_4', 'Bob Johnson', 1200, 1300, 'Pupil', 'Specialist', 'UK', 'London', 'Cambridge', 'avatar4.jpg', 10, 0),
('admin_user', 'admin@example.com', 'hashed_admin_password', 'System Admin', 0, 0, 'Newbie', 'Newbie', 'International', 'Virtual', 'Codeforces', 'admin.jpg', 500, 1);
GO

-- 获取插入的用户ID
DECLARE @admin_id BIGINT;
SELECT @admin_id = user_id FROM Users WHERE handle = 'admin_user';
GO

-- 2. 插入比赛数据
INSERT INTO CONTEST (name, type, phase, start_time, duration_seconds, website_url, description, difficulty, kind, icpc_region, country, city, season, created_by)
VALUES 
('Codeforces Round #1000 (Div. 1)', 'CF', 'FINISHED', '2024-01-15 14:00:00', 7200, 'https://codeforces.com/contest/1000', 'Celebratory Round #1000', 5, 'CF Round', 'Europe', 'Russia', 'Moscow', 'Winter 2024', (SELECT user_id FROM Users WHERE handle = 'admin_user')),
('ICPC World Finals 2024', 'ICPC', 'FINISHED', '2024-03-20 09:00:00', 18000, 'https://icpc.global/finals', 'ICPC World Finals', 5, 'ICPC Finals', 'Global', 'Egypt', 'Sharm El-Sheikh', '2024', (SELECT user_id FROM Users WHERE handle = 'admin_user')),
('Educational Codeforces Round 200', 'CF', 'FINISHED', '2024-02-10 17:00:00', 7200, 'https://codeforces.com/contest/200', 'Educational Round', 3, 'Educational', 'Global', 'Virtual', 'Online', 'Winter 2024', (SELECT user_id FROM Users WHERE handle = 'admin_user'));
GO

-- 3. 插入题目数据
DECLARE @contest1_id BIGINT, @contest2_id BIGINT, @contest3_id BIGINT;
SELECT @contest1_id = contest_id FROM CONTEST WHERE name = 'Codeforces Round #1000 (Div. 1)';
SELECT @contest2_id = contest_id FROM CONTEST WHERE name = 'ICPC World Finals 2024';
SELECT @contest3_id = contest_id FROM CONTEST WHERE name = 'Educational Codeforces Round 200';
INSERT INTO PROBLEM (problem_id, contest_id, problem_index, title, statement, input_specification, output_specification, sample_tests, time_limit_ms, memory_limit_kb, difficulty, accepted_count, submission_count)
VALUES 
('CF1000A', @contest1_id, 'A', 'Watermelon', 'One hot summer day Pete and his friend Billy decided to buy a watermelon...', 'The first (and the only) input line contains integer number w (1 ≤ w ≤ 100)...', 'Print YES, if the boys can divide the watermelon into two parts...', '[{"input": "8", "output": "YES"}, {"input": "5", "output": "NO"}]', 1000, 256000, '800', 15000, 25000),
('CF1000B', @contest1_id, 'B', 'Prime Subtraction', 'You are given two integers x and y. You can perform multiple operations...', 'The first line contains a single integer t (1 ≤ t ≤ 1000) — the number of test cases...', 'For each test case, print "YES" if you can make x equal to y...', '[{"input": "4\n100 98\n42 32\n100 100\n100 97", "output": "YES\nYES\nYES\nNO"}]', 2000, 512000, '1200', 8000, 15000),
('CF1000C', @contest1_id, 'C', 'Complex Problem', 'This is a more complex problem for the contest...', 'Input format description...', 'Output format description...', '[{"input": "1\n2", "output": "3"}]', 3000, 1048576, '1800', 5000, 12000),
('EDU200A', @contest3_id, 'A', 'Educational Problem A', 'Educational problem statement...', 'Educational input specification...', 'Educational output specification...', '[{"input": "test", "output": "result"}]', 1500, 256000, '1000', 8000, 15000);
GO

-- 4. 插入题目标签数据
INSERT INTO PROBLEM_TAG (name, description)
VALUES 
('math', 'Problems involving mathematical concepts and calculations'),
('greedy', 'Problems that can be solved using greedy algorithms'),
('dp', 'Dynamic programming problems'),
('graphs', 'Problems related to graph theory'),
('implementation', 'Problems that require careful implementation'),
('brute force', 'Problems solvable by trying all possibilities');
GO

-- 5. 插入题目标签关系数据
INSERT INTO PROBLEM_TAG_RELATION (problem_id, tag_id)
SELECT p.problem_id, pt.tag_id
FROM PROBLEM p
CROSS APPLY (
    VALUES 
    ('CF1000A', 'math'), ('CF1000A', 'implementation'),
    ('CF1000B', 'math'), ('CF1000B', 'greedy'),
    ('CF1000C', 'dp'), ('CF1000C', 'graphs'),
    ('EDU200A', 'implementation'), ('EDU200A', 'brute force')
) AS v(pid, tag_name)
JOIN PROBLEM_TAG pt ON pt.name = v.tag_name
WHERE p.problem_id = v.pid;
GO

-- 6. 插入测试用例数据
INSERT INTO TEST_CASE (problem_id, input_data, expected_output, is_sample, test_order)
VALUES 
('CF1000A', '8', 'YES', 1, 1),
('CF1000A', '5', 'NO', 1, 2),
('CF1000A', '10', 'YES', 0, 3),
('CF1000A', '3', 'NO', 0, 4),
('CF1000B', '4', 'YES', 1, 1),
('CF1000B', '100 98', 'YES', 0, 2),
('CF1000C', '1', '3', 1, 1),
('EDU200A', 'test', 'result', 1, 1);
-- 7. 插入提交数据、比赛用户关系和Hack数据
DECLARE @contest1_id BIGINT;
SELECT @contest1_id = contest_id FROM CONTEST WHERE name = 'Codeforces Round #1000 (Div. 1)';

-- 插入提交数据
INSERT INTO SUBMISSION (user_id, problem_id, contest_id, programming_language, source_code, source_length, verdict, time_consumed_ms, memory_consumed_kb, passed_test_count, submission_time, points)
VALUES 
((SELECT user_id FROM Users WHERE handle = 'tourist'), 'CF1000A', @contest1_id, 'GNU C++17', '#include <iostream>
using namespace std;
int main() { int w; cin >> w; cout << (w % 2 == 0 && w > 2 ? "YES" : "NO"); return 0; }', 98, 'ACCEPTED', 15, 4000, 4, '2024-01-15 14:05:00', 100),
((SELECT user_id FROM Users WHERE handle = 'petr'), 'CF1000A', @contest1_id, 'Java 11', 'import java.util.*; public class Main { public static void main(String[] args) { Scanner sc = new Scanner(System.in); int w = sc.nextInt(); System.out.println(w % 2 == 0 && w > 2 ? "YES" : "NO"); } }', 150, 'ACCEPTED', 78, 16384, 4, '2024-01-15 14:06:00', 100),
((SELECT user_id FROM Users WHERE handle = 'alice'), 'CF1000A', @contest1_id, 'Python 3', 'w = int(input())
print("YES" if w % 2 == 0 and w > 2 else "NO")', 56, 'WRONG_ANSWER', 30, 8192, 2, '2024-01-15 14:07:00', 0);

-- 插入比赛用户关系数据
INSERT INTO CONTEST_USER (contest_id, user_id, role, rating_before, rating_after, contest_rank, solved_count, total_penalty, scores)
VALUES 
(@contest1_id, (SELECT user_id FROM Users WHERE handle = 'tourist'), 'contestant', 3480, 3500, 1, 5, 120, 4500),
(@contest1_id, (SELECT user_id FROM Users WHERE handle = 'petr'), 'contestant', 3180, 3200, 2, 4, 180, 4200),
(@contest1_id, (SELECT user_id FROM Users WHERE handle = 'alice'), 'contestant', 1580, 1600, 150, 2, 450, 1800),
(@contest1_id, (SELECT user_id FROM Users WHERE handle = 'bob'), 'contestant', 1180, 1200, 300, 1, 600, 800);

-- 插入Hack数据

INSERT INTO HACK (hacker_id, defender_id, problem_id, contest_id, verdict, test_case, hack_result)
VALUES 
((SELECT user_id FROM Users WHERE handle = 'tourist'), (SELECT user_id FROM Users WHERE handle = 'alice'), 'CF1000A', @contest1_id, 'SUCCESSFUL', '7', 'Expected: NO, Received: YES'),
((SELECT user_id FROM Users WHERE handle = 'petr'), (SELECT user_id FROM Users WHERE handle = 'bob'), 'CF1000A', @contest1_id, 'UNSUCCESSFUL', '2', 'Expected: NO, Received: NO - Hack failed');

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