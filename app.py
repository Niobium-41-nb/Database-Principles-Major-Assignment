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
                   p.memory_limit_kb, p.difficulty, c.name as contest_name
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
        
        problem_data = {
            'problem_id': problem[0],
            'title': problem[1],
            'statement': problem[2],
            'input_specification': problem[3],
            'output_specification': problem[4],
            'sample_tests': problem[5],
            'time_limit': problem[6],
            'memory_limit': problem[7],
            'difficulty': problem[8],
            'contest_name': problem[9],
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
                   country, city, organization, registration_time
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
                'registration_time': row[10].strftime('%Y-%m-%d %H:%M:%S')
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)