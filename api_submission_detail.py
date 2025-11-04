@app.route('/api/submission/<int:submission_id>')
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
        # 查询是否有关联的Hack
        cursor.execute('''
            SELECT h.hack_id, u1.handle AS hacker, h.verdict, h.hack_time, h.hack_result
            FROM HACK h
            JOIN Users u1 ON h.hacker_id = u1.user_id
            WHERE h.defender_id = (SELECT user_id FROM Users WHERE handle = ?) AND h.problem_id = ?
        ''', (row[1], row[11]))
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
