# codeforces_crawler_fixed.py
import pyodbc
import requests
import json
import random
import string
import time
from datetime import datetime, timedelta


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
                        # 检查提交记录中是否包含必要的字段
                        if 'problem' not in submission or 'contestId' not in submission['problem']:
                            continue
                            
                        problem_id = f"{submission['problem']['contestId']}{submission['problem']['index']}"

                        # 检查题目是否存在
                        self.cursor.execute("SELECT problem_id FROM PROBLEM WHERE problem_id = ?", problem_id)
                        if not self.cursor.fetchone():
                            continue

                        # 处理比赛ID：如果不在有效比赛ID中，设为NULL
                        contest_id = submission.get('contestId')
                        if contest_id is None or contest_id not in valid_contest_ids:
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

                        # 处理可能缺失的字段
                        time_consumed_ms = submission.get('timeConsumedMillis', 0)
                        memory_consumed_bytes = submission.get('memoryConsumedBytes', 0)
                        memory_consumed_kb = memory_consumed_bytes // 1024 if memory_consumed_bytes else 0
                        passed_test_count = submission.get('passedTestCount', 0)
                        creation_time = submission.get('creationTimeSeconds', time.time())
                        relative_time = submission.get('relativeTimeSeconds', 0)

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
                                            time_consumed_ms,
                                            memory_consumed_kb,
                                            passed_test_count,
                                            datetime.fromtimestamp(creation_time),
                                            relative_time
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

    def insert_contest_users(self, crawler):
        """插入比赛用户关系数据"""
        inserted_count = 0
        print("开始插入比赛用户关系数据...")
        
        # 获取用户列表
        self.cursor.execute("SELECT user_id, handle FROM Users")
        users = self.cursor.fetchall()
        
        if not users:
            print("没有找到用户数据，跳过比赛用户关系插入")
            return 0
        
        # 获取比赛列表
        self.cursor.execute("SELECT contest_id, name FROM CONTEST")
        contests = self.cursor.fetchall()
        
        if not contests:
            print("没有找到比赛数据，跳过比赛用户关系插入")
            return 0
        
        # 为每个比赛随机分配一些参与者
        for contest_id, contest_name in contests:
            try:
                # 确保不会选择超过用户总数的参与者
                participant_count = min(random.randint(5, 20), len(users))
                participants = random.sample(users, participant_count)
                
                for user_id, handle in participants:
                    try:
                        # 检查是否已存在该关系
                        self.cursor.execute("""
                            SELECT 1 FROM CONTEST_USER 
                            WHERE contest_id = ? AND user_id = ?
                        """, contest_id, user_id)
                        
                        if self.cursor.fetchone():
                            continue
                        
                        # 随机分配角色（大部分为参赛者）
                        roles = ['contestant'] * 8 + ['virtual'] * 1 + ['out_of_competition'] * 1
                        role = random.choice(roles)
                        
                        # 如果是前几个比赛，添加一些作者和测试者
                        if contest_id <= 5 and participants.index((user_id, handle)) < 3:
                            if random.random() < 0.3:
                                role = 'author'
                            elif random.random() < 0.5:
                                role = 'tester'
                        
                        # 获取用户当前评分
                        self.cursor.execute("SELECT rating FROM Users WHERE user_id = ?", user_id)
                        user_rating_result = self.cursor.fetchone()
                        rating_before = user_rating_result[0] if user_rating_result else 0
                        
                        # 模拟比赛后的评分变化（±0-200）
                        rating_change = random.randint(-50, 150)
                        rating_after = max(0, rating_before + rating_change)
                        
                        # 随机生成比赛排名
                        contest_rank = random.randint(1, len(participants))
                        
                        # 根据排名生成解题数量和罚时
                        max_solved = min(10, contest_rank // 2 + 1)
                        solved_count = random.randint(0, max_solved)
                        
                        # 罚时与解题数量和排名相关
                        base_penalty = solved_count * 1200  # 每道题基础罚时
                        rank_penalty = contest_rank * 10    # 排名相关的额外罚时
                        total_penalty = base_penalty + random.randint(-300, 300) + rank_penalty
                        
                        # 计算得分（与解题数量和排名相关）
                        scores = solved_count * 100 + max(0, 500 - contest_rank * 10)
                        
                        # 使用 timedelta（需要导入）
                        registration_time = datetime.now() - timedelta(days=random.randint(1, 365))
                        
                        self.cursor.execute("""
                            INSERT INTO CONTEST_USER (contest_id, user_id, registration_time, 
                                                role, rating_before, rating_after, 
                                                contest_rank, solved_count, total_penalty, scores)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, 
                                            contest_id,
                                            user_id,
                                            registration_time,
                                            role,
                                            rating_before,
                                            rating_after,
                                            contest_rank,
                                            solved_count,
                                            int(total_penalty),
                                            scores
                                            )
                        inserted_count += 1
                        
                        # 如果比赛已完成，更新用户的评分
                        if role == 'contestant' and rating_after != rating_before:
                            self.cursor.execute("""
                                UPDATE Users 
                                SET rating = ?, 
                                    max_rating = CASE WHEN ? > max_rating THEN ? ELSE max_rating END,
                                    user_rank = ?,
                                    max_rank = CASE WHEN ? > max_rating THEN ? ELSE max_rank END
                                WHERE user_id = ?
                            """, 
                                                rating_after,
                                                rating_after, rating_after,
                                                self.calculate_rank(rating_after),
                                                rating_after, self.calculate_rank(rating_after),
                                                user_id)
                            
                    except Exception as e:
                        print(f"插入用户 {handle} 到比赛 {contest_name} 错误: {e}")
                        continue
                        
            except Exception as e:
                print(f"处理比赛 {contest_name} 用户关系错误: {e}")
                continue
        
        self.conn.commit()
        print(f"成功插入 {inserted_count} 个比赛用户关系")
        return inserted_count

    

    def get_user_contest_history(self, user_id):
        """获取用户比赛历史"""
        try:
            self.cursor.execute("""
                SELECT c.name, c.start_time, cu.contest_rank, cu.solved_count,
                    cu.rating_before, cu.rating_after, cu.role
                FROM CONTEST_USER cu
                JOIN CONTEST c ON cu.contest_id = c.contest_id
                WHERE cu.user_id = ?
                ORDER BY c.start_time DESC
            """, user_id)
            
            history = self.cursor.fetchall()
            return history
        except Exception as e:
            print(f"获取用户比赛历史错误: {e}")
            return []

    def get_contest_standings(self, contest_id):
        """获取比赛排名"""
        try:
            self.cursor.execute("""
                SELECT 
                    u.handle, 
                    COALESCE(u.name, u.handle) as display_name,  -- 如果name为NULL，使用handle
                    cu.contest_rank, 
                    cu.solved_count, 
                    cu.total_penalty, 
                    cu.scores, 
                    cu.rating_before, 
                    cu.rating_after,
                    cu.role
                FROM CONTEST_USER cu
                JOIN Users u ON cu.user_id = u.user_id
                WHERE cu.contest_id = ?
                ORDER BY cu.contest_rank ASC
            """, contest_id)
            
            standings = self.cursor.fetchall()
            return standings
        except Exception as e:
            print(f"获取比赛排名错误: {e}")
            return []

    def display_contest_standings(self, contest_id):
        """显示比赛排名（更好的格式化输出）"""
        standings = self.get_contest_standings(contest_id)
        if not standings:
            print(f"比赛 {contest_id} 没有找到排名数据")
            return
        
        print(f"\n=== 比赛 {contest_id} 排名 ===")
        print(f"{'排名':<4} {'用户名':<20} {'显示名':<20} {'解题数':<6} {'罚时':<8} {'得分':<6} {'角色':<15}")
        print("-" * 85)
        
        for standing in standings[:10]:  # 只显示前10名
            handle, display_name, rank, solved, penalty, score, rating_before, rating_after, role = standing
            
            # 处理可能的None值
            handle = handle or "Unknown"
            display_name = display_name or handle
            solved = solved or 0
            penalty = penalty or 0
            score = score or 0
            role = role or "contestant"
            
            print(f"{rank:<4} {handle:<20} {display_name:<20} {solved:<6} {penalty:<8} {score:<6} {role:<15}")


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
        users = crawler.get_users(20000)
        if users:
            db_manager.insert_users(users)

        # 2. 爬取并插入比赛数据
        contests = crawler.get_contests()
        if contests:
            db_manager.insert_contests(contests[:5000])  # 减少比赛数量以便测试

        # 3. 爬取并插入题目数据
        problems, stats = crawler.get_problems()
        if problems:
            db_manager.insert_problems(problems[:10000], stats)  # 减少题目数量以便测试

        # 4. 插入比赛用户关系
        db_manager.insert_contest_users(crawler)

        # 5. 插入提交记录
        # db_manager.insert_submissions(crawler)

        print("=== 数据爬取和插入完成 ===")

        # 显示统计信息
        print("\n=== 统计信息 ===")
        
        # 检查数据是否成功插入
        db_manager.cursor.execute("SELECT COUNT(*) FROM Users")
        user_count = db_manager.cursor.fetchone()[0]
        print(f"总用户数: {user_count}")
        
        db_manager.cursor.execute("SELECT COUNT(*) FROM CONTEST")
        contest_count = db_manager.cursor.fetchall()[0]
        print(f"总比赛数: {contest_count}")
        
        db_manager.cursor.execute("SELECT COUNT(*) FROM CONTEST_USER")
        contest_user_count = db_manager.cursor.fetchone()[0]
        print(f"总比赛参与记录: {contest_user_count}")
        
        # 获取第一个比赛并显示排名
        db_manager.cursor.execute("SELECT TOP 1 contest_id, name FROM CONTEST")
        first_contest = db_manager.cursor.fetchone()
        if first_contest:
            contest_id, contest_name = first_contest
            print(f"\n显示比赛 '{contest_name}' (ID: {contest_id}) 的排名:")
            db_manager.display_contest_standings(contest_id)
        else:
            print("没有找到比赛数据")

    except Exception as e:
        print(f"程序执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_manager.close()


if __name__ == "__main__":
    main()