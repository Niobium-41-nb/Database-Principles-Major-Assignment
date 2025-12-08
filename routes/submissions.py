"""
提交管理路由模块

该模块处理代码提交相关的API端点，包括：
- 提交代码评测
- 获取提交记录列表和详情
- 提交结果查询和Hack关联
- 提交统计和过滤功能
"""

from flask import Blueprint, request, jsonify, session, render_template
import random
from utils.database import get_db_connection

submissions_bp = Blueprint('submissions', __name__)


@submissions_bp.route('/submission/<int:submission_id>')
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
            return render_template('submission_detail.html', not_found=True, detail=None, hack=None)
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
        # 查询是否有关联的Hack - 根据实际数据库结构修正
        cursor.execute('''
            SELECT h.hack_id, u1.handle AS hacker, h.verdict, h.hack_time, h.hack_result
            FROM HACK h
            JOIN Users u1 ON h.hacker_id = u1.user_id
            WHERE h.submission_id = ?
        ''', (submission_id,))
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
        return render_template('submission_detail.html', detail=detail, hack=hack, error=None)
    except Exception as e:
        return render_template('submission_detail.html', error=str(e), detail=None, hack=None, not_found=False)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@submissions_bp.route('/api/submission/<int:submission_id>')
def api_submission_detail(submission_id):
    """获取提交记录详情（含Hack信息）"""
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
            return jsonify({'success': False, 'message': '提交记录不存在'})
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
        # 查询是否有关联的Hack - 根据实际数据库结构修正
        cursor.execute('''
            SELECT h.hack_id, u1.handle AS hacker, h.verdict, h.hack_time, h.hack_result
            FROM HACK h
            JOIN Users u1 ON h.hacker_id = u1.user_id
            WHERE h.submission_id = ?
        ''', (submission_id,))
        hack_row = cursor.fetchone()
        if hack_row:
            detail['hack'] = {
                'hack_id': hack_row[0],
                'hacker': hack_row[1],
                'verdict': hack_row[2],
                'hack_time': hack_row[3].strftime('%Y-%m-%d %H:%M:%S'),
                'hack_result': hack_row[4]
            }
        return jsonify({'success': True, 'detail': detail})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@submissions_bp.route('/api/submit', methods=['POST'])
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

        # 移除更新题目统计信息的代码，因为字段已被移除
        # 统计信息现在通过查询动态计算

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


@submissions_bp.route('/api/submissions')
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
            # 查询该提交是否被Hack - 根据实际数据库结构修正
            hack_id = None
            try:
                cursor2 = conn.cursor()
                cursor2.execute('''
                    SELECT hack_id FROM HACK WHERE submission_id = ?
                ''', (row[0],))
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