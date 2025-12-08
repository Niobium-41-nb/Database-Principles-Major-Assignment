"""
题目管理路由模块

该模块处理题目相关的API端点，包括：
- 获取题目列表和详情
- 题目统计信息查询
- 创建新题目（管理员功能）
- 题目标签和测试用例管理
"""

from flask import Blueprint, request, jsonify, session
import json
from utils.database import get_db_connection

problems_bp = Blueprint('problems', __name__)

def get_problem_statistics(problem_id):
    """获取题目的统计信息（提交数和AC数）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取总提交数
        cursor.execute("""
            SELECT COUNT(*) 
            FROM SUBMISSION 
            WHERE problem_id = ?
        """, (problem_id,))
        submission_count = cursor.fetchone()[0]
        
        # 获取AC数
        cursor.execute("""
            SELECT COUNT(*) 
            FROM SUBMISSION 
            WHERE problem_id = ? AND verdict = 'Accepted'
        """, (problem_id,))
        accepted_count = cursor.fetchone()[0]
        
        return submission_count, accepted_count
        
    except Exception as e:
        print(f"获取题目统计信息失败: {str(e)}")
        return 0, 0
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@problems_bp.route('/api/problems')
def get_problems():
    """获取题目列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.problem_id, p.title, p.difficulty, 
                   p.time_limit_ms, p.memory_limit_kb, c.name as contest_name
            FROM PROBLEM p
            LEFT JOIN CONTEST c ON p.contest_id = c.contest_id
            WHERE p.is_visible = 1
            ORDER BY p.problem_id
        """)
        
        problems = []
        for row in cursor.fetchall():
            problem_id = row[0]
            submission_count, accepted_count = get_problem_statistics(problem_id)
            
            problems.append({
                'problem_id': problem_id,
                'title': row[1],
                'difficulty': row[2],
                'accepted_count': accepted_count,
                'submission_count': submission_count,
                'time_limit': row[3],
                'memory_limit': row[4],
                'contest_name': row[5]
            })
        
        return jsonify({'success': True, 'problems': problems})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取题目失败: {str(e)}'})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@problems_bp.route('/api/problem/<problem_id>')
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

        # 解析样例数据
        sample_tests = []
        if problem[5]:  # sample_tests 字段
            try:
                sample_tests = json.loads(problem[5])
            except:
                # 如果解析失败，使用默认样例
                sample_tests = [{"input": "1 2", "output": "3"}]

        # 获取统计信息
        submission_count, accepted_count = get_problem_statistics(problem_id)

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
            'accepted_count': accepted_count,
            'submission_count': submission_count,
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

@problems_bp.route('/api/problems/create', methods=['POST'])
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

        # 插入题目基本信息 (移除了accepted_count和submission_count字段)
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