from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pyodbc
import json
import random
from datetime import datetime, timedelta
import config

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# 数据库配置 - Windows身份验证
DB_CONFIG = {
    'server': config.DB_SERVER,
    'database': config.DB_NAME,
    'trusted_connection': 'yes',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

def get_db_connection():
    """获取数据库连接 - Windows身份验证"""
    conn_str = f"DRIVER={DB_CONFIG['driver']};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};Trusted_Connection=yes"
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"数据库连接失败: {str(e)}")
        raise

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/problems')
def problems():
    """题目列表页面"""
    return render_template('problems.html')

@app.route('/contests')
def contests():
    """比赛列表页面"""
    return render_template('contests.html')

@app.route('/submissions')
def submissions():
    """提交记录页面"""
    return render_template('submissions.html')

@app.route('/users')
def users():
    """用户列表页面"""
    return render_template('users.html')

@app.route('/profile')
def profile():
    """用户个人资料页面"""
    return render_template('profile.html')

# API 路由
@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.json
    handle = data.get('handle')
    email = data.get('email')
    password = data.get('password')
    name = data.get('name', '')
    
    if not handle or not email or not password:
        return jsonify({'success': False, 'message': '请填写完整信息'})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查用户名和邮箱是否已存在
        cursor.execute("SELECT user_id FROM Users WHERE handle = ? OR email = ?", (handle, email))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': '用户名或邮箱已存在'})
        
        # 插入新用户
        cursor.execute("""
            INSERT INTO Users (handle, email, password, name, registration_time, last_online_time)
            VALUES (?, ?, ?, ?, GETDATE(), GETDATE())
        """, (handle, email, password, name))
        
        conn.commit()
        return jsonify({'success': True, 'message': '注册成功'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json
    handle = data.get('handle')
    password = data.get('password')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, handle, name, rating, user_rank, is_admin 
            FROM Users 
            WHERE handle = ? AND password = ? AND is_active = 1
        """, (handle, password))
        
        user = cursor.fetchone()
        if user:
            session['user_id'] = user[0]
            session['handle'] = user[1]
            session['name'] = user[2]
            session['rating'] = user[3]
            session['rank'] = user[4]
            session['is_admin'] = user[5]
            
            # 更新最后在线时间
            cursor.execute("UPDATE Users SET last_online_time = GETDATE() WHERE user_id = ?", user[0])
            conn.commit()
            
            return jsonify({
                'success': True, 
                'message': '登录成功',
                'user': {
                    'user_id': user[0],
                    'handle': user[1],
                    'name': user[2],
                    'rating': user[3],
                    'rank': user[4],
                    'is_admin': user[5]
                }
            })
        else:
            return jsonify({'success': False, 'message': '用户名或密码错误'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/logout')
def logout():
    """用户登出"""
    session.clear()
    return jsonify({'success': True, 'message': '登出成功'})

@app.route('/problem/<problem_id>')
def problem_detail(problem_id):
    """题目详情页面"""
    # 传递一些基本变量给模板，避免模板渲染错误
    return render_template('problem_detail.html',
                         problem={'title': '加载中...', 'difficulty': '简单'},
                         difficulty_color='secondary')

@app.route('/api/problems')
def get_problems():
    """获取题目列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.problem_id, p.title, p.difficulty, p.accepted_count, p.submission_count,
                   p.time_limit_ms, p.memory_limit_kb, c.name as contest_name
            FROM PROBLEM p
            LEFT JOIN CONTEST c ON p.contest_id = c.contest_id
            WHERE p.is_visible = 1
            ORDER BY p.problem_id
        """)
        
        problems = []
        for row in cursor.fetchall():
            problems.append({
                'problem_id': row[0],
                'title': row[1],
                'difficulty': row[2],
                'accepted_count': row[3],
                'submission_count': row[4],
                'time_limit': row[5],
                'memory_limit': row[6],
                'contest_name': row[7]
            })
        
        return jsonify({'success': True, 'problems': problems})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取题目失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/api/problem/<problem_id>')
def get_problem_detail(problem_id):
    """获取题目详情"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取题目基本信息
        cursor.execute("""
            SELECT p.problem_id, p.title, p.statement, p.input_specification, 
                   p.output_specification, p.sample_tests, p.time_limit_ms, 
                   p.memory_limit_kb, p.difficulty, p.accepted_count, p.submission_count,
                   c.name as contest_name
            FROM PROBLEM p
            LEFT JOIN CONTEST c ON p.contest_id = c.contest_id
            WHERE p.problem_id = ? AND p.is_visible = 1
        """, (problem_id,))

        problem = cursor.fetchone()
        if not problem:
            return jsonify({'success': False, 'message': '题目不存在'})

        # 获取题目标签
        cursor.execute("""
            SELECT t.name 
            FROM PROBLEM_TAG t
            INNER JOIN PROBLEM_TAG_RELATION r ON t.tag_id = r.tag_id
            WHERE r.problem_id = ?
        """, (problem_id,))

        tags = [row[0] for row in cursor.fetchall()]

        # 解析样例数据
        sample_tests = []
        if problem[5]:  # sample_tests 字段
            try:
                sample_tests = json.loads(problem[5])
            except:
                # 如果解析失败，使用默认样例
                sample_tests = [{"input": "1 2", "output": "3"}]

        problem_data = {
            'problem_id': problem[0],
            'title': problem[1],
            'statement': problem[2],
            'input_specification': problem[3],
            'output_specification': problem[4],
            'sample_tests': sample_tests,
            'time_limit': problem[6],
            'memory_limit': problem[7],
            'difficulty': problem[8],
            'accepted_count': problem[9],
            'submission_count': problem[10],
            'contest_name': problem[11],
            'tags': tags
        }

        return jsonify({'success': True, 'problem': problem_data})

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取题目详情失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/submit', methods=['POST'])
def submit_solution():
    """提交代码"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})
    
    data = request.json
    problem_id = data.get('problem_id')
    source_code = data.get('source_code')
    language = data.get('language', 'C++')
    
    if not problem_id or not source_code:
        return jsonify({'success': False, 'message': '请填写完整信息'})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查题目是否存在
        cursor.execute("SELECT problem_id FROM PROBLEM WHERE problem_id = ? AND is_visible = 1", (problem_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '题目不存在'})
        
        # 插入提交记录
        cursor.execute("""
            INSERT INTO SUBMISSION (user_id, problem_id, programming_language, source_code, source_length, submission_time)
            VALUES (?, ?, ?, ?, ?, GETDATE())
        """, (session['user_id'], problem_id, language, source_code, len(source_code)))
        
        submission_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]
        
        # 模拟评测过程
        verdicts = ['ACCEPTED', 'WRONG_ANSWER', 'TIME_LIMIT_EXCEEDED', 'MEMORY_LIMIT_EXCEEDED', 'RUNTIME_ERROR']
        weights = [40, 30, 10, 10, 10]  # 不同结果的权重
        
        verdict = random.choices(verdicts, weights=weights)[0]
        time_consumed = random.randint(0, 2000)
        memory_consumed = random.randint(1000, 256000)
        passed_tests = random.randint(0, 10)
        
        cursor.execute("""
            UPDATE SUBMISSION 
            SET verdict = ?, time_consumed_ms = ?, memory_consumed_kb = ?, passed_test_count = ?
            WHERE submission_id = ?
        """, (verdict, time_consumed, memory_consumed, passed_tests, submission_id))
        
        # 更新题目统计信息
        cursor.execute("UPDATE PROBLEM SET submission_count = submission_count + 1 WHERE problem_id = ?", (problem_id,))
        if verdict == 'ACCEPTED':
            cursor.execute("UPDATE PROBLEM SET accepted_count = accepted_count + 1 WHERE problem_id = ?", (problem_id,))
        
        conn.commit()
        
        return jsonify({
            'success': True, 
            'message': '提交成功',
            'submission_id': submission_id,
            'verdict': verdict
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'提交失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/submissions')
def get_submissions():
    """获取提交记录"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = request.args.get('user_id')
        problem_id = request.args.get('problem_id')
        
        query = """
            SELECT s.submission_id, u.handle, p.title, s.programming_language, 
                   s.verdict, s.time_consumed_ms, s.memory_consumed_kb, 
                   s.passed_test_count, s.submission_time
            FROM SUBMISSION s
            INNER JOIN Users u ON s.user_id = u.user_id
            INNER JOIN PROBLEM p ON s.problem_id = p.problem_id
            WHERE 1=1
        """
        params = []
        
        if user_id:
            query += " AND s.user_id = ?"
            params.append(user_id)
        
        if problem_id:
            query += " AND s.problem_id = ?"
            params.append(problem_id)
        
        query += " ORDER BY s.submission_time DESC"
        
        cursor.execute(query, params)
        
        submissions = []
        for row in cursor.fetchall():
            submissions.append({
                'submission_id': row[0],
                'handle': row[1],
                'problem_title': row[2],
                'language': row[3],
                'verdict': row[4],
                'time_consumed': row[5],
                'memory_consumed': row[6],
                'passed_tests': row[7],
                'submission_time': row[8].strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({'success': True, 'submissions': submissions})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取提交记录失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/contests')
def get_contests():
    """获取比赛列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT contest_id, name, type, phase, start_time, duration_seconds, 
                   difficulty, kind, icpc_region
            FROM CONTEST
            ORDER BY start_time DESC
        """)
        
        contests = []
        for row in cursor.fetchall():
            end_time = row[4] + timedelta(seconds=row[5])
            contests.append({
                'contest_id': row[0],
                'name': row[1],
                'type': row[2],
                'phase': row[3],
                'start_time': row[4].strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'duration': row[5],
                'difficulty': row[6],
                'kind': row[7],
                'region': row[8]
            })
        
        return jsonify({'success': True, 'contests': contests})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取比赛列表失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/users')
def get_users():
    """获取用户列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, handle, name, rating, max_rating, user_rank, max_rank,
                   country, city, organization, registration_time, is_admin
            FROM Users
            WHERE is_active = 1
            ORDER BY rating DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'user_id': row[0],
                'handle': row[1],
                'name': row[2],
                'rating': row[3],
                'max_rating': row[4],
                'rank': row[5],
                'max_rank': row[6],
                'country': row[7],
                'city': row[8],
                'organization': row[9],
                'registration_time': row[10].strftime('%Y-%m-%d %H:%M:%S'),
                'is_admin': row[11]  # 添加管理员信息
            })
        
        return jsonify({'success': True, 'users': users})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户列表失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/contest/<contest_id>/standings')
def get_contest_standings(contest_id):
    """获取比赛排名"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.handle, u.rating, cu.contest_rank, cu.solved_count, cu.total_penalty, cu.scores
            FROM CONTEST_USER cu
            INNER JOIN Users u ON cu.user_id = u.user_id
            WHERE cu.contest_id = ?
            ORDER BY cu.contest_rank
        """, (contest_id,))
        
        standings = []
        for row in cursor.fetchall():
            standings.append({
                'handle': row[0],
                'rating': row[1],
                'rank': row[2],
                'solved_count': row[3],
                'penalty': row[4],
                'score': row[5]
            })
        
        return jsonify({'success': True, 'standings': standings})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取比赛排名失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/user/current')
def get_current_user():
    """获取当前登录用户信息"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '用户未登录'})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, handle, email, name, rating, max_rating, user_rank, max_rank,
                   country, city, organization, avatar, registration_time, last_online_time,
                   contribution, is_admin
            FROM Users
            WHERE user_id = ? AND is_active = 1
        """, (session['user_id'],))
        
        user = cursor.fetchone()
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'})
        
        user_data = {
            'user_id': user[0],
            'handle': user[1],
            'email': user[2],
            'name': user[3],
            'rating': user[4],
            'max_rating': user[5],
            'rank': user[6],
            'max_rank': user[7],
            'country': user[8],
            'city': user[9],
            'organization': user[10],
            'avatar': user[11],
            'registration_time': user[12].strftime('%Y-%m-%d %H:%M:%S'),
            'last_online_time': user[13].strftime('%Y-%m-%d %H:%M:%S'),
            'contribution': user[14],
            'is_admin': user[15]
        }
        
        return jsonify({'success': True, 'user': user_data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户详情失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/user/<user_id>')
def get_user_detail(user_id):
    """获取用户详情"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, handle, email, name, rating, max_rating, user_rank, max_rank,
                   country, city, organization, avatar, registration_time, last_online_time,
                   contribution, is_admin
            FROM Users
            WHERE user_id = ? AND is_active = 1
        """, (user_id,))
        
        user = cursor.fetchone()
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'})
        
        user_data = {
            'user_id': user[0],
            'handle': user[1],
            'email': user[2],
            'name': user[3],
            'rating': user[4],
            'max_rating': user[5],
            'rank': user[6],
            'max_rank': user[7],
            'country': user[8],
            'city': user[9],
            'organization': user[10],
            'avatar': user[11],
            'registration_time': user[12].strftime('%Y-%m-%d %H:%M:%S'),
            'last_online_time': user[13].strftime('%Y-%m-%d %H:%M:%S'),
            'contribution': user[14],
            'is_admin': user[15]
        }
        
        return jsonify({'success': True, 'user': user_data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户详情失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/api/user/update', methods=['POST'])
def update_user_profile():
    """更新用户个人信息"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})

    data = request.json
    user_id = session['user_id']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 构建更新字段和参数
        update_fields = []
        params = []

        allowed_fields = ['name', 'country', 'city', 'organization', 'avatar']
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])

        # 如果没有要更新的字段
        if not update_fields:
            return jsonify({'success': False, 'message': '没有要更新的信息'})

        # 添加用户ID参数
        params.append(user_id)

        # 执行更新
        update_query = f"UPDATE Users SET {', '.join(update_fields)} WHERE user_id = ?"
        cursor.execute(update_query, params)

        # 更新session中的用户信息
        if 'name' in data:
            session['name'] = data['name']

        conn.commit()

        return jsonify({'success': True, 'message': '个人信息更新成功'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/api/user/change_password', methods=['POST'])
def change_password():
    """修改密码"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})

    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    user_id = session['user_id']

    if not old_password or not new_password:
        return jsonify({'success': False, 'message': '请填写完整信息'})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 验证旧密码
        cursor.execute("SELECT user_id FROM Users WHERE user_id = ? AND password = ?", (user_id, old_password))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '原密码错误'})

        # 更新密码
        cursor.execute("UPDATE Users SET password = ? WHERE user_id = ?", (new_password, user_id))
        conn.commit()

        return jsonify({'success': True, 'message': '密码修改成功'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'密码修改失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/create-problem')
def create_problem_page():
    """题目创建页面"""
    return render_template('create_problem.html')


@app.route('/api/problems/create', methods=['POST'])
def create_problem():
    """创建题目"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})

    # 检查是否是管理员
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '只有管理员可以创建题目'})

    data = request.json

    required_fields = ['problem_id', 'title', 'statement', 'time_limit', 'memory_limit']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'字段 {field} 不能为空'})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查题目ID是否已存在
        cursor.execute("SELECT problem_id FROM PROBLEM WHERE problem_id = ?", (data['problem_id'],))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': '题目ID已存在'})

        # 插入题目基本信息
        cursor.execute("""
            INSERT INTO PROBLEM (
                problem_id, title, statement, input_specification, output_specification,
                time_limit_ms, memory_limit_kb, difficulty, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['problem_id'],
            data['title'],
            data.get('statement', ''),
            data.get('input_specification', ''),
            data.get('output_specification', ''),
            data['time_limit'],
            data['memory_limit'],
            data.get('difficulty', '简单'),
            data.get('notes', '')
        ))

        # 处理标签
        tags = data.get('tags', [])
        for tag_name in tags:
            # 检查标签是否存在
            cursor.execute("SELECT tag_id FROM PROBLEM_TAG WHERE name = ?", (tag_name,))
            tag_row = cursor.fetchone()

            if tag_row:
                tag_id = tag_row[0]
            else:
                # 创建新标签
                cursor.execute("INSERT INTO PROBLEM_TAG (name) VALUES (?)", (tag_name,))
                tag_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]

            # 建立题目标签关系
            cursor.execute(
                "INSERT INTO PROBLEM_TAG_RELATION (problem_id, tag_id) VALUES (?, ?)",
                (data['problem_id'], tag_id)
            )

        # 处理测试用例
        test_cases = data.get('test_cases', [])
        sample_tests = []

        for i, test_case in enumerate(test_cases):
            cursor.execute("""
                INSERT INTO TEST_CASE (problem_id, input_data, expected_output, is_sample, test_order)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data['problem_id'],
                test_case['input'],
                test_case['output'],
                test_case.get('is_sample', False),
                test_case.get('test_order', i + 1)
            ))

            # 收集样例测试用于存储到problem表
            if test_case.get('is_sample', False):
                sample_tests.append({
                    'input': test_case['input'],
                    'output': test_case['output']
                })

        # 更新题目的sample_tests字段
        if sample_tests:
            cursor.execute(
                "UPDATE PROBLEM SET sample_tests = ? WHERE problem_id = ?",
                (json.dumps(sample_tests), data['problem_id'])
            )

        conn.commit()
        return jsonify({'success': True, 'message': '题目创建成功'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'创建题目失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/api/user/set_admin', methods=['POST'])
def set_admin():
    """设置用户管理员权限"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})

    # 检查当前用户是否是管理员
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '只有管理员可以设置管理员权限'})

    data = request.json
    target_user_id = data.get('user_id')
    is_admin = data.get('is_admin', False)

    if not target_user_id:
        return jsonify({'success': False, 'message': '用户ID不能为空'})

    # 不能修改自己的管理员权限
    if target_user_id == session['user_id']:
        return jsonify({'success': False, 'message': '不能修改自己的管理员权限'})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查目标用户是否存在
        cursor.execute("SELECT user_id FROM Users WHERE user_id = ? AND is_active = 1", (target_user_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '用户不存在'})

        # 更新管理员权限
        cursor.execute("UPDATE Users SET is_admin = ? WHERE user_id = ?", (is_admin, target_user_id))
        conn.commit()

        action = "设为" if is_admin else "取消"
        return jsonify({'success': True, 'message': f'用户已{action}管理员'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'设置管理员权限失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/create-contest')
def create_contest_page():
    """比赛创建页面"""
    return render_template('create_contest.html')


@app.route('/api/contests/create', methods=['POST'])
def create_contest():
    """创建比赛"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})

    # 检查是否是管理员
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '只有管理员可以创建比赛'})

    data = request.json

    required_fields = ['name', 'start_time', 'duration_seconds']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'字段 {field} 不能为空'})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 处理日期时间格式
        start_time_str = data['start_time']
        try:
            # 将前端传来的 datetime-local 格式转换为 SQL Server 可识别的格式
            # 前端格式: "YYYY-MM-DDTHH:MM"
            # 转换为: "YYYY-MM-DD HH:MM:SS"
            if 'T' in start_time_str:
                start_time_str = start_time_str.replace('T', ' ') + ':00'
        except Exception as e:
            return jsonify({'success': False, 'message': f'日期时间格式错误: {str(e)}'})

        # 插入比赛信息
        cursor.execute("""
            INSERT INTO CONTEST (
                name, type, phase, start_time, duration_seconds, 
                description, difficulty, kind, icpc_region, country, city, season, created_by
            ) VALUES (?, ?, ?, CONVERT(DATETIME2, ?), ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['name'],
            data.get('type', 'CF'),
            data.get('phase', 'BEFORE'),
            start_time_str,  # 使用转换后的日期时间字符串
            data['duration_seconds'],
            data.get('description', ''),
            data.get('difficulty', 0),
            data.get('kind', ''),
            data.get('icpc_region', ''),
            data.get('country', ''),
            data.get('city', ''),
            data.get('season', ''),
            session['user_id']
        ))

        contest_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]

        conn.commit()
        return jsonify({
            'success': True,
            'message': '比赛创建成功',
            'contest_id': contest_id
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'创建比赛失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/contest/<contest_id>')
def contest_detail(contest_id):
    """比赛详情页面"""
    return render_template('contest_detail.html', contest_id=contest_id)


@app.route('/contest/<contest_id>/standings')
def contest_standings_page(contest_id):
    """比赛排名页面"""
    return render_template('contest_standings.html', contest_id=contest_id)


@app.route('/api/contest/<contest_id>')
def get_contest_detail(contest_id):
    """获取比赛详情"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT contest_id, name, type, phase, start_time, duration_seconds,
                   description, difficulty, kind, icpc_region, country, city, season
            FROM CONTEST
            WHERE contest_id = ?
        """, (contest_id,))

        contest = cursor.fetchone()
        if not contest:
            return jsonify({'success': False, 'message': '比赛不存在'})

        # 计算结束时间
        start_time = contest[4]
        duration = contest[5]
        end_time = start_time + timedelta(seconds=duration)

        contest_data = {
            'contest_id': contest[0],
            'name': contest[1],
            'type': contest[2],
            'phase': contest[3],
            'start_time': contest[4].strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': contest[5],
            'description': contest[6],
            'difficulty': contest[7],
            'kind': contest[8],
            'icpc_region': contest[9],
            'country': contest[10],
            'city': contest[11],
            'season': contest[12]
        }

        return jsonify({'success': True, 'contest': contest_data})

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取比赛详情失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/api/contest/<contest_id>/problems')
def get_contest_problems(contest_id):
    """获取比赛题目列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT problem_id, title, difficulty, time_limit_ms, memory_limit_kb
            FROM PROBLEM
            WHERE contest_id = ? AND is_visible = 1
            ORDER BY problem_index
        """, (contest_id,))

        problems = []
        for row in cursor.fetchall():
            problems.append({
                'problem_id': row[0],
                'title': row[1],
                'difficulty': row[2],
                'time_limit': row[3],
                'memory_limit': row[4]
            })

        return jsonify({'success': True, 'problems': problems})

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取比赛题目失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)