"""
比赛管理路由模块

该模块处理比赛相关的API端点，包括：
- 获取比赛列表和详情
- 获取比赛排名和题目列表
- 创建比赛和用户报名
- 比赛统计信息查询
"""

from flask import Blueprint, request, jsonify, session
from datetime import timedelta
from utils.database import get_db_connection

contests_bp = Blueprint('contests', __name__)

@contests_bp.route('/api/contests')
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

@contests_bp.route('/api/contest/<contest_id>')
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

@contests_bp.route('/api/contest/<contest_id>/standings')
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
                'username': handle,
                'rating': rating,
                'contest_rank': contest_rank or rank,
                'solved_count': solved_count or 0,
                'penalty': total_penalty or 0,
                'total_score': scores or 0,
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

@contests_bp.route('/api/contest/<contest_id>/problems')
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

@contests_bp.route('/api/contests/create', methods=['POST'])
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
            start_time_str,
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

@contests_bp.route('/api/contest/<contest_id>/register', methods=['POST'])
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