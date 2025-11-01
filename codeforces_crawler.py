# codeforces_crawler_fixed.py
import pyodbc
import requests
import json
import random
import string
import time
from datetime import datetime


class CodeforcesCrawler:
    def __init__(self):
        self.base_url = "https://codeforces.com/api/"

    def get_users(self, count=100):
        """获取用户数据"""
        try:
            print("正在获取用户数据...")
            response = requests.get(f"{self.base_url}user.ratedList?activeOnly=true")
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'OK':
                    users = data['result'][:count]
                    print(f"成功获取 {len(users)} 个用户")
                    return users
            print("获取用户数据失败")
            return []
        except Exception as e:
            print(f"获取用户数据错误: {e}")
            return []

    def get_contests(self):
        """获取比赛数据"""
        try:
            print("正在获取比赛数据...")
            response = requests.get(f"{self.base_url}contest.list")
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'OK':
                    contests = data['result']
                    print(f"成功获取 {len(contests)} 个比赛")
                    return contests
            print("获取比赛数据失败")
            return []
        except Exception as e:
            print(f"获取比赛数据错误: {e}")
            return []

    def get_problems(self):
        """获取题目数据"""
        try:
            print("正在获取题目数据...")
            response = requests.get(f"{self.base_url}problemset.problems")
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'OK':
                    problems = data['result']['problems']
                    stats = data['result']['problemStatistics']
                    print(f"成功获取 {len(problems)} 个题目")
                    return problems, stats
            print("获取题目数据失败")
            return [], []
        except Exception as e:
            print(f"获取题目数据错误: {e}")
            return [], []

    def get_user_submissions(self, handle, count=50):
        """获取用户提交记录"""
        try:
            print(f"正在获取用户 {handle} 的提交记录...")
            response = requests.get(f"{self.base_url}user.status?handle={handle}&count={count}")
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'OK':
                    submissions = data['result']
                    print(f"成功获取用户 {handle} 的 {len(submissions)} 条提交记录")
                    return submissions
            print(f"获取用户 {handle} 提交记录失败")
            return []
        except Exception as e:
            print(f"获取用户 {handle} 提交记录错误: {e}")
            return []


class DatabaseManager:
    def __init__(self):
        self.conn = self.get_db_connection()
        self.cursor = self.conn.cursor()
        self.existing_tags_cache = {}  # 缓存已存在的标签

    def get_db_connection(self):
        """使用 Windows 身份验证连接 SQL Server"""
        try:
            # Windows 身份验证连接字符串
            connection_string = (
                'DRIVER={ODBC Driver 17 for SQL Server};'
                'SERVER=localhost;'  # 修改为您的服务器地址
                'DATABASE=OJ;'
                'Trusted_Connection=yes;'
            )
            conn = pyodbc.connect(connection_string)
            print("成功连接到数据库")
            return conn
        except Exception as e:
            print(f"数据库连接错误: {e}")
            raise

    def generate_random_password(self, length=12):
        """生成随机密码"""
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    def calculate_rank(self, rating):
        """根据评分计算等级"""
        if rating is None or rating < 1200:
            return "Newbie"
        elif rating < 1400:
            return "Pupil"
        elif rating < 1600:
            return "Specialist"
        elif rating < 1900:
            return "Expert"
        elif rating < 2100:
            return "Candidate Master"
        elif rating < 2300:
            return "Master"
        elif rating < 2400:
            return "International Master"
        elif rating < 2600:
            return "Grandmaster"
        elif rating < 3000:
            return "International Grandmaster"
        else:
            return "Legendary Grandmaster"

    def insert_users(self, users_data):
        """插入用户数据"""
        inserted_count = 0
        print("开始插入用户数据...")

        for user in users_data:
            try:
                # 检查用户是否已存在
                self.cursor.execute("SELECT user_id FROM Users WHERE handle = ?", user['handle'])
                if self.cursor.fetchone():
                    continue

                password = self.generate_random_password()
                rating = user.get('rating', 0)
                max_rating = user.get('maxRating', 0)

                # 计算用户等级
                user_rank = self.calculate_rank(rating)
                max_rank = self.calculate_rank(max_rating)

                # 处理可能为空的字段
                first_name = user.get('firstName', '')
                last_name = user.get('lastName', '')
                full_name = f"{first_name} {last_name}".strip()
                if not full_name:
                    full_name = user['handle']

                registration_time = datetime.fromtimestamp(user.get('registrationTimeSeconds', time.time()))
                last_online_time = datetime.fromtimestamp(user.get('lastOnlineTimeSeconds', time.time()))

                self.cursor.execute("""
                    INSERT INTO Users (handle, email, password, name, rating, max_rating, 
                                    user_rank, max_rank, country, city, organization, 
                                    registration_time, last_online_time, contribution)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                                    user['handle'],
                                    f"{user['handle']}@codeforces.com",
                                    password,
                                    full_name,
                                    rating,
                                    max_rating,
                                    user_rank,
                                    max_rank,
                                    user.get('country', ''),
                                    user.get('city', ''),
                                    user.get('organization', ''),
                                    registration_time,
                                    last_online_time,
                                    user.get('contribution', 0)
                                    )
                inserted_count += 1

            except Exception as e:
                print(f"插入用户 {user['handle']} 错误: {e}")
                continue

        self.conn.commit()
        print(f"成功插入 {inserted_count} 个用户")
        return inserted_count

    def insert_contests(self, contests_data):
        """插入比赛数据"""
        inserted_count = 0
        print("开始插入比赛数据...")

        # 先获取一个管理员用户ID作为创建者
        self.cursor.execute("SELECT TOP 1 user_id FROM Users WHERE is_admin = 1 OR user_id = 1")
        admin_user = self.cursor.fetchone()
        created_by = admin_user[0] if admin_user else 1

        for contest in contests_data:
            try:
                # 检查比赛是否已存在
                self.cursor.execute("SELECT contest_id FROM CONTEST WHERE name = ?", contest['name'])
                if self.cursor.fetchone():
                    continue

                # 处理比赛阶段
                phase = contest.get('phase', 'FINISHED')
                if phase == 'BEFORE':
                    phase = 'BEFORE'
                elif phase == 'FINISHED':
                    phase = 'FINISHED'
                else:
                    phase = 'CODING'

                start_time = datetime.fromtimestamp(contest.get('startTimeSeconds', time.time()))

                self.cursor.execute("""
                    INSERT INTO CONTEST (name, type, phase, frozen, start_time, 
                                      duration_seconds, website_url, description, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                                    contest['name'],
                                    contest.get('type', 'CF'),
                                    phase,
                                    contest.get('frozen', False),
                                    start_time,
                                    contest.get('durationSeconds', 7200),  # 默认2小时
                                    f"https://codeforces.com/contest/{contest['id']}",
                                    contest.get('description', f"Codeforces Contest {contest['id']}"),
                                    created_by
                                    )
                inserted_count += 1

            except Exception as e:
                print(f"插入比赛 {contest['name']} 错误: {e}")
                continue

        self.conn.commit()
        print(f"成功插入 {inserted_count} 个比赛")
        return inserted_count

    def load_existing_tags(self):
        """加载已存在的标签到缓存"""
        try:
            self.cursor.execute("SELECT tag_id, name FROM PROBLEM_TAG")
            for row in self.cursor.fetchall():
                self.existing_tags_cache[row[1]] = row[0]
            print(f"已加载 {len(self.existing_tags_cache)} 个标签到缓存")
        except Exception as e:
            print(f"加载标签缓存错误: {e}")

    def insert_problems(self, problems_data, problem_stats):
        """插入题目数据"""
        inserted_count = 0
        print("开始插入题目数据...")

        # 加载已存在的标签
        self.load_existing_tags()

        # 首先获取所有比赛ID映射
        contest_map = {}
        try:
            self.cursor.execute("SELECT contest_id, name FROM CONTEST")
            for row in self.cursor.fetchall():
                contest_name = row[1]
                # 尝试从比赛名称中提取数字ID
                import re
                numbers = re.findall(r'\d+', contest_name)
                if numbers:
                    contest_map[int(numbers[-1])] = row[0]
        except Exception as e:
            print(f"获取比赛映射错误: {e}")

        # 用于记录已处理的标签关系，避免重复
        processed_tag_relations = set()

        for i, problem in enumerate(problems_data):
            try:
                problem_id = f"{problem['contestId']}{problem['index']}"

                # 检查题目是否已存在
                self.cursor.execute("SELECT problem_id FROM PROBLEM WHERE problem_id = ?", problem_id)
                if self.cursor.fetchone():
                    continue

                # 获取对应的统计信息
                stats = next((s for s in problem_stats if
                              s['contestId'] == problem['contestId'] and s['index'] == problem['index']), {})

                contest_id = contest_map.get(problem.get('contestId'), None)

                self.cursor.execute("""
                    INSERT INTO PROBLEM (problem_id, contest_id, problem_index, title, 
                                      time_limit_ms, memory_limit_kb, difficulty,
                                      accepted_count, submission_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                                    problem_id,
                                    contest_id,
                                    problem['index'],
                                    problem['name'],
                                    problem.get('timeLimitMillis', 2000),
                                    problem.get('memoryLimitBytes', 256000) // 1024,
                                    problem.get('rating', 0),
                                    stats.get('solvedCount', 0),
                                    stats.get('solvedCount', 0) + random.randint(0, 100)
                                    )
                inserted_count += 1

                # 插入标签（使用缓存和去重）
                for tag in problem.get('tags', []):
                    relation_key = (problem_id, tag)
                    if relation_key not in processed_tag_relations:
                        self.insert_problem_tag_safe(problem_id, tag)
                        processed_tag_relations.add(relation_key)

            except Exception as e:
                print(f"插入题目 {problem.get('name', 'Unknown')} 错误: {e}")
                continue

        self.conn.commit()
        print(f"成功插入 {inserted_count} 个题目")
        return inserted_count

    def insert_problem_tag_safe(self, problem_id, tag_name):
        """安全插入题目标签（避免重复）"""
        try:
            # 检查标签是否在缓存中
            if tag_name in self.existing_tags_cache:
                tag_id = self.existing_tags_cache[tag_name]
            else:
                # 插入新标签
                self.cursor.execute("INSERT INTO PROBLEM_TAG (name) VALUES (?)", tag_name)
                self.cursor.execute("SELECT @@IDENTITY")
                tag_id = self.cursor.fetchone()[0]
                self.existing_tags_cache[tag_name] = tag_id

            # 检查标签关系是否已存在
            self.cursor.execute("""
                SELECT 1 FROM PROBLEM_TAG_RELATION 
                WHERE problem_id = ? AND tag_id = ?
            """, problem_id, tag_id)

            if not self.cursor.fetchone():
                # 插入标签关系
                self.cursor.execute("""
                    INSERT INTO PROBLEM_TAG_RELATION (problem_id, tag_id)
                    VALUES (?, ?)
                """, problem_id, tag_id)

        except Exception as e:
            # 如果是重复键错误，忽略它
            if 'PRIMARY KEY' in str(e) or '2627' in str(e):
                pass  # 忽略重复键错误
            else:
                print(f"插入标签错误: {e}")

    def insert_submissions(self, crawler):
        """插入提交记录"""
        inserted_count = 0
        print("开始插入提交记录...")

        # 获取用户列表
        self.cursor.execute("SELECT user_id, handle FROM Users")
        users = self.cursor.fetchall()

        # 获取有效的比赛ID集合
        valid_contest_ids = set()
        self.cursor.execute("SELECT contest_id FROM CONTEST")
        for row in self.cursor.fetchall():
            valid_contest_ids.add(row[0])

        for user_id, handle in users:
            try:
                submissions = crawler.get_user_submissions(handle, 10)  # 每个用户获取10条记录

                for submission in submissions:
                    try:
                        problem_id = f"{submission['problem']['contestId']}{submission['problem']['index']}"

                        # 检查题目是否存在
                        self.cursor.execute("SELECT problem_id FROM PROBLEM WHERE problem_id = ?", problem_id)
                        if not self.cursor.fetchone():
                            continue

                        # 处理比赛ID：如果不在有效比赛ID中，设为NULL
                        contest_id = submission.get('contestId')
                        if contest_id not in valid_contest_ids:
                            contest_id = None

                        # 映射判决结果到新的格式
                        verdict_map = {
                            'OK': 'Accepted',
                            'WRONG_ANSWER': 'Wrong Answer',
                            'TIME_LIMIT_EXCEEDED': 'Time Limit Exceeded',
                            'MEMORY_LIMIT_EXCEEDED': 'Memory Limit Exceeded',
                            'RUNTIME_ERROR': 'Runtime Error',
                            'COMPILATION_ERROR': 'Compilation Error',
                            'PRESENTATION_ERROR': 'Presentation Error',
                            'FAILED': 'Failed',
                            'PARTIAL': 'Partial Solution',
                            'CHALLENGED': 'Challenged',
                            'SKIPPED': 'Skipped',
                            'REJECTED': 'Rejected',
                            'IDLENESS_LIMIT_EXCEEDED': 'Idleness Limit Exceeded'
                        }

                        verdict = verdict_map.get(submission.get('verdict', ''), 'Pending')

                        self.cursor.execute("""
                            INSERT INTO SUBMISSION (user_id, problem_id, contest_id, 
                                                 programming_language, source_code, 
                                                 source_length, verdict, time_consumed_ms,
                                                 memory_consumed_kb, passed_test_count,
                                                 submission_time, relative_time)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                                            user_id,
                                            problem_id,
                                            contest_id,  # 可能为NULL
                                            submission.get('programmingLanguage', 'Unknown'),
                                            f"// Source code for {problem_id} by {handle}",
                                            len(f"// Source code for {problem_id} by {handle}"),
                                            verdict,
                                            submission.get('timeConsumedMillis', 0),
                                            submission.get('memoryConsumedBytes', 0) // 1024 if submission.get(
                                                'memoryConsumedBytes') else 0,
                                            submission.get('passedTestCount', 0),
                                            datetime.fromtimestamp(submission.get('creationTimeSeconds', time.time())),
                                            submission.get('relativeTimeSeconds', 0)
                                            )
                        inserted_count += 1

                    except Exception as e:
                        # 如果是外键约束错误，忽略它
                        if 'FOREIGN KEY' in str(e) or '547' in str(e):
                            continue
                        else:
                            print(f"插入提交记录错误: {e}")
                        continue

            except Exception as e:
                print(f"获取用户 {handle} 提交记录错误: {e}")
                continue

        self.conn.commit()
        print(f"成功插入 {inserted_count} 个提交记录")
        return inserted_count

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("数据库连接已关闭")


def main():
    print("=== Codeforces 数据爬取程序开始 ===")

    crawler = CodeforcesCrawler()
    db_manager = DatabaseManager()

    try:
        # 1. 爬取并插入用户数据
        users = crawler.get_users(2000)  # 获取20个用户
        if users:
            db_manager.insert_users(users)

        # 2. 爬取并插入比赛数据
        contests = crawler.get_contests()
        if contests:
            db_manager.insert_contests(contests[:3000])  # 插入前30个比赛

        # 3. 爬取并插入题目数据
        problems, stats = crawler.get_problems()
        if problems:
            db_manager.insert_problems(problems[:50000], stats)  # 插入前50个题目

        # 4. 插入提交记录
        db_manager.insert_submissions(crawler)

        print("=== 数据爬取和插入完成 ===")

    except Exception as e:
        print(f"程序执行过程中发生错误: {e}")
    finally:
        db_manager.close()


if __name__ == "__main__":
    main()