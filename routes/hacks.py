"""
Hack管理路由模块

该模块处理Hack相关的API端点，包括：
- 获取Hack记录列表
- 获取特定Hack的详细提交信息
- 提交新的Hack测试
- Hack结果评判和Rating更新
"""

from flask import Blueprint, request, jsonify, session
import json
import random
from utils.database import get_db_connection

hacks_bp = Blueprint('hacks', __name__)

@hacks_bp.route('/api/hacks')
def api_hacks():
    """获取所有Hack记录"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT h.hack_id, 
                   hacker.handle AS hacker, 
                   defender.handle AS defender, 
                   s.problem_id, 
                   s.contest_id, 
                   h.verdict, 
                   h.hack_time, 
                   h.hack_result,
                   p.title AS problem_title,
                   c.name AS contest_name
            FROM HACK h
            JOIN SUBMISSION s ON h.submission_id = s.submission_id
            JOIN Users hacker ON h.hacker_id = hacker.user_id
            JOIN Users defender ON s.user_id = defender.user_id
            JOIN PROBLEM p ON s.problem_id = p.problem_id
            LEFT JOIN CONTEST c ON s.contest_id = c.contest_id
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
                'hack_result': row[7],
                'problem_title': row[8],
                'contest_name': row[9]
            })
        return jsonify({'success': True, 'hacks': hacks})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@hacks_bp.route('/api/hack/<int:hack_id>/submissions')
def api_hack_submissions(hack_id):
    """获取某个Hack的详细提交"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取Hack的详细信息
        cursor.execute('''
            SELECT h.verdict, 
                   p.title as problem_title, 
                   c.name as contest_name,
                   hacker.handle as hacker_name, 
                   defender.handle as defender_name,
                   s.submission_id,
                   s.problem_id,
                   s.contest_id
            FROM HACK h
            JOIN SUBMISSION s ON h.submission_id = s.submission_id
            JOIN PROBLEM p ON s.problem_id = p.problem_id
            LEFT JOIN CONTEST c ON s.contest_id = c.contest_id
            JOIN Users hacker ON h.hacker_id = hacker.user_id
            JOIN Users defender ON s.user_id = defender.user_id
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
            'defender': hack_row[4],
            'submission_id': hack_row[5],
            'problem_id': hack_row[6],
            'contest_id': hack_row[7]
        }
        
        # 获取被Hack的提交记录详情
        cursor.execute('''
            SELECT s.submission_id, u.handle, s.programming_language, s.verdict, 
                   s.submission_time, s.points, s.time_consumed_ms, s.memory_consumed_kb,
                   s.source_code
            FROM SUBMISSION s
            JOIN Users u ON s.user_id = u.user_id
            WHERE s.submission_id = ?
        ''', (hack_status['submission_id'],))
        
        submission_row = cursor.fetchone()
        submission = None
        if submission_row:
            submission = {
                'submission_id': submission_row[0],
                'defender': submission_row[1],
                'language': submission_row[2],
                'verdict': submission_row[3],
                'submission_time': submission_row[4].strftime('%Y-%m-%d %H:%M:%S'),
                'points': submission_row[5],
                'time_consumed': submission_row[6],
                'memory_consumed': submission_row[7],
                'source_code': submission_row[8]
            }
            
        return jsonify({
            'success': True, 
            'hack_status': hack_status['verdict'],
            'hack_details': hack_status,
            'submission': submission  # 现在只返回被Hack的特定提交
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@hacks_bp.route('/api/hack/<int:submission_id>', methods=['POST'])
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
        
        # 检查是否已经Hack过这个提交
        cursor.execute("""
            SELECT hack_id FROM HACK 
            WHERE hacker_id = ? AND submission_id = ?
        """, (session['user_id'], submission_id))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'message': '你已经Hack过这个提交'})
        
        # 插入Hack记录
        cursor.execute("""
            INSERT INTO HACK (hacker_id, submission_id, verdict, test_case, hack_time)
            VALUES (?, ?, ?, ?, GETDATE())
        """, (session['user_id'], submission_id, 'INVALID', 
              json.dumps({'input': input_data, 'output': output_data})))
        
        hack_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]
        
        # 评判Hack结果（这里简化处理，使用随机结果）
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
