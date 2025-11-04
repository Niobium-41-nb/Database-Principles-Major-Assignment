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

# Hack相关页面
@app.route('/hacks')
def hacks():
    """Hack记录页面"""
    return render_template('hacks.html')

@app.route('/hack/<int:hack_id>/submissions')
def hack_submissions(hack_id):
    """某个Hack的提交详情页面"""
    return render_template('hack_submissions.html', hack_id=hack_id)

@app.route('/users')
def users():
    """用户列表页面"""
    return render_template('users.html')

@app.route('/profile')
def profile():
    """用户个人资料页面"""
    return render_template('profile.html')

# API 路由
@app.route('/submission/<int:submission_id>')
def submission_detail(submission_id):
    """提交详情页面"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.submission_id, u.handle, p.title, s.programming_language, s.source_code, s.verdict, s.time_consumed_ms, s.memory_consumed_kb, s.passed_test_count, s.submission_time, s.points, s.problem_id
            FROM SUBMISSION s
            JOIN Users u ON s.user_id = u.user_id
            JOIN PROBLEM p ON s.problem_id = p.problem_id
            WHERE s.submission_id = ?
        ''', (submission_id,))
        row = cursor.fetchone()
        if not row:
            return render_template('submission_detail.html', not_found=True)
        detail = {
            'submission_id': row[0],
            'handle': row[1],
            'problem_title': row[2],
            'language': row[3],
            'source_code': row[4],
            'verdict': row[5],
            'time_consumed': row[6],
            'memory_consumed': row[7],
            'passed_tests': row[8],
            'submission_time': row[9].strftime('%Y-%m-%d %H:%M:%S'),
            'points': row[10]
        }
        # 查询是否有关联的Hack
        cursor.execute('''
            SELECT h.hack_id, u1.handle AS hacker, h.verdict, h.hack_time, h.hack_result
            FROM HACK h
            JOIN Users u1 ON h.hacker_id = u1.user_id
            WHERE h.defender_id = (SELECT user_id FROM Users WHERE handle = ?) AND h.problem_id = ?
        ''', (row[1], row[11]))
        hack_row = cursor.fetchone()
        hack = None
        if hack_row:
            hack = {
                'hack_id': hack_row[0],
                'hacker': hack_row[1],
                'verdict': hack_row[2],
                'hack_time': hack_row[3].strftime('%Y-%m-%d %H:%M:%S'),
                'hack_result': hack_row[4]
            }
        return render_template('submission_detail.html', detail=detail, hack=hack)
    except Exception as e:
        return render_template('submission_detail.html', error=str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
@app.route('/api/hacks')
def api_hacks():
    """获取所有Hack记录"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT h.hack_id, u1.handle AS hacker, u2.handle AS defender, h.problem_id, h.contest_id, h.verdict, h.hack_time, h.hack_result
            FROM HACK h
            JOIN Users u1 ON h.hacker_id = u1.user_id
            JOIN Users u2 ON h.defender_id = u2.user_id
            ORDER BY h.hack_time DESC
        ''')
        hacks = []
        for row in cursor.fetchall():
            hacks.append({
                'hack_id': row[0],
                'hacker': row[1],
                'defender': row[2],
                'problem_id': row[3],
                'contest_id': row[4],
                'verdict': row[5],
                'hack_time': row[6].strftime('%Y-%m-%d %H:%M:%S'),
                'hack_result': row[7]
            })
        return jsonify({'success': True, 'hacks': hacks})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/hack/<int:hack_id>/submissions')
def api_hack_submissions(hack_id):
    """获取某个Hack的详细提交"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 首先获取Hack的状态
        cursor.execute('''
            SELECT h.verdict, p.title as problem_title, c.name as contest_name,
                   hacker.handle as hacker_name, defender.handle as defender_name
            FROM HACK h
            JOIN PROBLEM p ON h.problem_id = p.problem_id
            LEFT JOIN CONTEST c ON h.contest_id = c.contest_id
            JOIN Users hacker ON h.hacker_id = hacker.user_id
            JOIN Users defender ON h.defender_id = defender.user_id
            WHERE h.hack_id = ?
        ''', (hack_id,))
        
        hack_row = cursor.fetchone()
        if not hack_row:
            return jsonify({'success': False, 'message': 'Hack记录不存在'})
            
        hack_status = {
            'verdict': hack_row[0],
            'problem_title': hack_row[1],
            'contest_name': hack_row[2],
            'hacker': hack_row[3],
            'defender': hack_row[4]
        }
        
        # 然后获取相关的提交记录
        cursor.execute('''
            SELECT s.submission_id, u.handle, s.programming_language, s.verdict, 
                   s.submission_time, s.points, s.time_consumed_ms, s.memory_consumed_kb
            FROM SUBMISSION s
            JOIN HACK h ON s.problem_id = h.problem_id AND s.contest_id = h.contest_id 
                      AND s.user_id = h.defender_id
            JOIN Users u ON s.user_id = u.user_id
            WHERE h.hack_id = ?
            ORDER BY s.submission_time DESC
        ''', (hack_id,))
        
        submissions = []
        for row in cursor.fetchall():
            submissions.append({
                'submission_id': row[0],
                'defender': row[1],
                'language': row[2],
                'verdict': row[3],
                'submission_time': row[4].strftime('%Y-%m-%d %H:%M:%S'),
                'points': row[5],
                'time_consumed': row[6],
                'memory_consumed': row[7]
            })
            
        return jsonify({
            'success': True, 
            'hack_status': hack_status['verdict'],  # 直接返回verdict字符串而不是整个对象
            'hack_details': hack_status,  # 保留完整的hack详情
            'submissions': submissions
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
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
        
        # 评测结果和权重
        verdicts = ['Accepted', 'Wrong Answer', 'Time Limit Exceeded', 'Memory Limit Exceeded', 'Runtime Error',
                   'Compilation Error', 'Idleness Limit Exceeded', 'Presentation Error', 'Partial Solution']
        weights = [35, 25, 8, 8, 8, 6, 4, 4, 2]  # 不同结果的权重
        
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
        if verdict == 'Accepted':
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
        
        user_handle = request.args.get('user_handle')
        problem_title = request.args.get('problem_title')
        verdict = request.args.get('verdict')
        
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
        
        if user_handle:
            query += " AND u.handle LIKE ?"
            params.append(f'%{user_handle}%')
        
        if problem_title:
            query += " AND p.title LIKE ?"
            params.append(f'%{problem_title}%')
        
        if verdict:
            query += " AND s.verdict = ?"
            params.append(verdict)
        
        query += " ORDER BY s.submission_time DESC"
        
        cursor.execute(query, params)
        
        submissions = []
        for row in cursor.fetchall():
            # 查询该提交是否被Hack
            hack_id = None
            try:
                cursor2 = conn.cursor()
                cursor2.execute('''SELECT hack_id FROM HACK WHERE defender_id = (SELECT user_id FROM Users WHERE handle = ?) AND problem_id = (SELECT problem_id FROM PROBLEM WHERE title = ?)''', (row[1], row[2]))
                hack_row = cursor2.fetchone()
                if hack_row:
                    hack_id = hack_row[0]
                cursor2.close()
            except:
                hack_id = None
            verdict = row[4]
            if hack_id:
                verdict = 'Hack'
            submissions.append({
                'submission_id': row[0],
                'handle': row[1],
                'problem_title': row[2],
                'language': row[3],
                'verdict': verdict,
                'time_consumed': row[5],
                'memory_consumed': row[6],
                'passed_tests': row[7],
                'submission_time': row[8].strftime('%Y-%m-%d %H:%M:%S'),
                'hack_id': hack_id
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

        # 首先验证contest_id是否为数字
        if not contest_id.isdigit():
            return jsonify({'success': False, 'message': '比赛ID格式错误'})
        contest_id_int = int(contest_id)

        # 获取比赛信息
        cursor.execute("SELECT name, phase FROM CONTEST WHERE contest_id = ?", (contest_id_int,))
        contest = cursor.fetchone()
        if not contest:
            return jsonify({'success': False, 'message': '比赛不存在'})
        contest_name, contest_phase = contest

        # 获取参赛用户及其排名
        cursor.execute("""
            SELECT
                u.handle,
                u.rating,
                cu.contest_rank,
                cu.solved_count,
                cu.total_penalty,
                cu.scores,
                cu.rating_before,
                cu.rating_after
            FROM CONTEST_USER cu
            INNER JOIN Users u ON cu.user_id = u.user_id
            WHERE cu.contest_id = ? AND cu.role = 'contestant'
            ORDER BY
                CASE
                    WHEN cu.contest_rank IS NOT NULL THEN cu.contest_rank
                    ELSE 999999
                END,
                cu.solved_count DESC,
                cu.total_penalty ASC
        """, (contest_id_int,))

        standings = []
        rank = 1
        for row in cursor.fetchall():
            handle, rating, contest_rank, solved_count, total_penalty, scores, rating_before, rating_after = row

            # 计算Rating变化
            rating_change = None
            if rating_after is not None and rating_before is not None:
                rating_change = rating_after - rating_before

            standings.append({
                'username': handle,  # 修改这里：将 'handle' 改为 'username'
                'rating': rating,
                'contest_rank': contest_rank or rank,
                'solved_count': solved_count or 0,
                'penalty': total_penalty or 0,
                'total_score': scores or 0,  # 同时修复这个字段名
                'rating_change': rating_change
            })
            rank += 1

        return jsonify({
            'success': True,
            'standings': standings,
            'contest_name': contest_name,
            'contest_phase': contest_phase
        })

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
        
        # 验证contest_id
        if not contest_id.isdigit():
            return jsonify({'success': False, 'message': '比赛ID格式错误'})
        
        contest_id_int = int(contest_id)

        cursor.execute("""
            SELECT problem_id, title, difficulty, time_limit_ms, memory_limit_kb
            FROM PROBLEM
            WHERE contest_id = ? AND is_visible = 1
            ORDER BY problem_index
        """, (contest_id_int,))

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

@app.route('/api/contest/<contest_id>/add_problem', methods=['POST'])
def add_problem_to_contest(contest_id):
    """添加题目到比赛"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})

    # 检查是否是管理员
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '只有管理员可以管理比赛题目'})

    data = request.json
    problem_id = data.get('problem_id')
    problem_index = data.get('problem_index', 'A')  # 默认题目索引为A

    if not problem_id:
        return jsonify({'success': False, 'message': '题目ID不能为空'})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查比赛是否存在
        cursor.execute("SELECT contest_id FROM CONTEST WHERE contest_id = ?", (contest_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '比赛不存在'})

        # 检查题目是否存在
        cursor.execute("SELECT problem_id, title FROM PROBLEM WHERE problem_id = ? AND is_visible = 1", (problem_id,))
        problem = cursor.fetchone()
        if not problem:
            return jsonify({'success': False, 'message': '题目不存在'})

        # 检查题目是否已经在比赛中
        cursor.execute("""
            SELECT problem_id FROM PROBLEM 
            WHERE contest_id = ? AND problem_id = ?
        """, (contest_id, problem_id))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': '题目已在此比赛中'})

        # 更新题目的比赛信息
        cursor.execute("""
            UPDATE PROBLEM 
            SET contest_id = ?, problem_index = ?
            WHERE problem_id = ?
        """, (contest_id, problem_index, problem_id))

        conn.commit()
        return jsonify({
            'success': True,
            'message': '题目添加成功',
            'problem': {
                'problem_id': problem_id,
                'title': problem[1],
                'index': problem_index
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'添加题目失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/contest/<contest_id>/remove_problem', methods=['POST'])
def remove_problem_from_contest(contest_id):
    """从比赛中移除题目"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})

    # 检查是否是管理员
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '只有管理员可以管理比赛题目'})

    data = request.json
    problem_id = data.get('problem_id')

    if not problem_id:
        return jsonify({'success': False, 'message': '题目ID不能为空'})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查题目是否在比赛中
        cursor.execute("""
            SELECT problem_id FROM PROBLEM 
            WHERE contest_id = ? AND problem_id = ?
        """, (contest_id, problem_id))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '题目不在此比赛中'})

        # 移除题目的比赛关联
        cursor.execute("""
            UPDATE PROBLEM 
            SET contest_id = NULL, problem_index = NULL
            WHERE problem_id = ?
        """, (problem_id,))

        conn.commit()
        return jsonify({'success': True, 'message': '题目移除成功'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'移除题目失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/contest/<contest_id>/available_problems')
def get_available_problems(contest_id):
    """获取可添加到比赛的题目列表（未在任何比赛中或仅在此比赛中的题目）"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})

    # 检查是否是管理员
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '只有管理员可以管理比赛题目'})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取所有可见的题目，包括不在任何比赛中的和在此比赛中的
        cursor.execute("""
            SELECT problem_id, title, difficulty, time_limit_ms, memory_limit_kb,
                   contest_id, problem_index
            FROM PROBLEM 
            WHERE is_visible = 1 AND (contest_id IS NULL OR contest_id = ?)
            ORDER BY 
                CASE WHEN contest_id = ? THEN 0 ELSE 1 END,  -- 当前比赛中的题目排在前面
                problem_id
        """, (contest_id, contest_id))

        problems = []
        for row in cursor.fetchall():
            problems.append({
                'problem_id': row[0],
                'title': row[1],
                'difficulty': row[2],
                'time_limit': row[3],
                'memory_limit': row[4],
                'in_contest': row[5] == int(contest_id) if row[5] else False,
                'problem_index': row[6]
            })

        return jsonify({'success': True, 'problems': problems})

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取题目列表失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/hack/<int:submission_id>', methods=['POST'])
def submit_hack(submission_id):
    """提交Hack"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})
    
    data = request.json
    input_data = data.get('input')
    output_data = data.get('output')
    
    if not input_data or not output_data:
        return jsonify({'success': False, 'message': '请提供完整的测试数据'})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取提交详情
        cursor.execute("""
            SELECT s.user_id, s.problem_id, s.contest_id, s.source_code, s.verdict,
                   u.handle, p.title
            FROM SUBMISSION s
            JOIN Users u ON s.user_id = u.user_id
            JOIN PROBLEM p ON s.problem_id = p.problem_id
            WHERE s.submission_id = ?
        """, (submission_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'message': '提交记录不存在'})
        
        defender_id, problem_id, contest_id, source_code, verdict, defender_handle, problem_title = row
        
        # 检查是否可以Hack
        if defender_id == session['user_id']:
            return jsonify({'success': False, 'message': '不能Hack自己的提交'})
        
        if verdict != 'Accepted':
            return jsonify({'success': False, 'message': '只能Hack通过的提交'})
        
        # 检查是否已经Hack过
        cursor.execute("""
            SELECT hack_id FROM HACK 
            WHERE hacker_id = ? AND defender_id = ? AND problem_id = ?
        """, (session['user_id'], defender_id, problem_id))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'message': '你已经Hack过这个用户在此题目上的提交'})
        
        # 插入Hack记录
        cursor.execute("""
            INSERT INTO HACK (hacker_id, defender_id, problem_id, contest_id, 
                            verdict, test_case, hack_time)
            VALUES (?, ?, ?, ?, ?, ?, GETDATE())
        """, (session['user_id'], defender_id, problem_id, contest_id,
              'INVALID', # 初始状态设为INVALID
              json.dumps({'input': input_data, 'output': output_data})))
        
        hack_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]
        
        # 评判Hack结果（这里简化处理，使用随机结果）
        import random
        hack_success = random.choice([True, False])
        hack_verdict = 'SUCCESSFUL' if hack_success else 'UNSUCCESSFUL'
        hack_result = '期望输出与实际输出不符' if hack_success else '期望输出与实际输出相符'
        
        # 更新Hack记录
        cursor.execute("""
            UPDATE HACK
            SET verdict = ?, hack_result = ?
            WHERE hack_id = ?
        """, (hack_verdict, hack_result, hack_id))
        
        # 如果Hack成功，更新用户Rating
        if hack_success:
            # 增加Hack成功者的Rating
            cursor.execute("""
                UPDATE Users
                SET rating = rating + 50
                WHERE user_id = ?
            """, (session['user_id'],))
            
            # 减少被Hack者的Rating
            cursor.execute("""
                UPDATE Users
                SET rating = rating - 50
                WHERE user_id = ?
            """, (defender_id,))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Hack提交成功',
            'hack_id': hack_id,
            'verdict': hack_verdict
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Hack提交失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/contest/<contest_id>/register', methods=['POST'])
def register_contest(contest_id):
    """用户报名参加比赛"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 验证contest_id
        if not contest_id.isdigit():
            return jsonify({'success': False, 'message': '比赛ID格式错误'})
        
        contest_id_int = int(contest_id)
        
        # 检查比赛是否存在
        cursor.execute("SELECT contest_id FROM CONTEST WHERE contest_id = ?", (contest_id_int,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '比赛不存在'})
        
        # 检查是否已经报名
        cursor.execute("""
            SELECT contest_id FROM CONTEST_USER 
            WHERE contest_id = ? AND user_id = ?
        """, (contest_id_int, session['user_id']))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'message': '已经报名参加此比赛'})
        
        # 获取用户当前rating
        cursor.execute("SELECT rating FROM Users WHERE user_id = ?", (session['user_id'],))
        user_rating = cursor.fetchone()[0]
        
        # 插入报名记录
        cursor.execute("""
            INSERT INTO CONTEST_USER (contest_id, user_id, registration_time, role, rating_before)
            VALUES (?, ?, GETDATE(), 'contestant', ?)
        """, (contest_id_int, session['user_id'], user_rating))
        
        conn.commit()
        return jsonify({'success': True, 'message': '报名成功'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'报名失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/contest/<contest_id>/generate_standings', methods=['POST'])
def generate_contest_standings(contest_id):
    """生成比赛排名（管理员功能）"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})
    
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '只有管理员可以生成排名'})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 验证contest_id
        if not contest_id.isdigit():
            return jsonify({'success': False, 'message': '比赛ID格式错误'})
        
        contest_id_int = int(contest_id)
        
        # 检查比赛是否存在
        cursor.execute("SELECT contest_id, start_time FROM CONTEST WHERE contest_id = ?", (contest_id_int,))
        contest = cursor.fetchone()
        if not contest:
            return jsonify({'success': False, 'message': '比赛不存在'})
        
        contest_id_db, start_time = contest
        
        # 获取比赛中的提交记录
        cursor.execute("""
            SELECT 
                s.user_id,
                s.problem_id,
                s.verdict,
                s.submission_time,
                s.points
            FROM SUBMISSION s
            WHERE s.contest_id = ?
            ORDER BY s.user_id, s.problem_id, s.submission_time
        """, (contest_id_int,))
        
        submissions = cursor.fetchall()
        
        # 获取参赛用户
        cursor.execute("""
            SELECT user_id FROM CONTEST_USER 
            WHERE contest_id = ? AND role = 'contestant'
        """, (contest_id_int,))
        
        contestants = [row[0] for row in cursor.fetchall()]
        
        if not contestants:
            return jsonify({'success': False, 'message': '没有参赛用户'})
        
        # 计算每个用户的解题情况
        user_stats = {}
        for user_id in contestants:
            user_stats[user_id] = {
                'solved_count': 0,
                'total_penalty': 0,
                'total_score': 0,
                'problems': {}
            }
        
        # 处理提交记录
        for submission in submissions:
            user_id, problem_id, verdict, submission_time, points = submission
            
            if user_id not in user_stats:
                continue
                
            if problem_id not in user_stats[user_id]['problems']:
                user_stats[user_id]['problems'][problem_id] = {
                    'solved': False,
                    'penalty': 0,
                    'submissions': 0,
                    'score': 0,
                    'solve_time': None
                }
            
            problem_stats = user_stats[user_id]['problems'][problem_id]
            
            if not problem_stats['solved']:
                problem_stats['submissions'] += 1
                
                if verdict == 'Accepted':
                    problem_stats['solved'] = True
                    # 计算解题时间（从比赛开始算起的分钟数）
                    solve_minutes = (submission_time - start_time).total_seconds() / 60
                    problem_stats['solve_time'] = solve_minutes
                    problem_stats['penalty'] = solve_minutes + (problem_stats['submissions'] - 1) * 20  # 每错误提交加20分钟罚时
                    
                    user_stats[user_id]['solved_count'] += 1
                    user_stats[user_id]['total_penalty'] += problem_stats['penalty']
                
                # 处理得分制比赛
                if points and points > problem_stats['score']:
                    problem_stats['score'] = points
        
        # 计算总分（对于得分制比赛）
        for user_id in user_stats:
            total_score = sum(problem['score'] for problem in user_stats[user_id]['problems'].values())
            user_stats[user_id]['total_score'] = total_score
        
        # 排序用户（按解题数降序，罚时升序）
        sorted_users = sorted(contestants, key=lambda uid: (
            -user_stats[uid]['solved_count'],
            user_stats[uid]['total_penalty']
        ))
        
        # 更新数据库中的排名
        current_rank = 1
        for user_id in sorted_users:
            stats = user_stats[user_id]
            cursor.execute("""
                UPDATE CONTEST_USER 
                SET contest_rank = ?, solved_count = ?, total_penalty = ?, scores = ?
                WHERE contest_id = ? AND user_id = ?
            """, (current_rank, stats['solved_count'], int(stats['total_penalty']), 
                  stats['total_score'], contest_id_int, user_id))
            current_rank += 1
        
        conn.commit()
        return jsonify({'success': True, 'message': '排名生成成功'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成排名失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)