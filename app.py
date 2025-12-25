"""
在线判题系统（OJ）主应用模块

该模块定义了Flask应用实例，配置了蓝图注册和基础页面路由。
提供了用户认证、题目管理、提交评测、比赛管理、用户管理和Hack功能。
"""

from flask import Flask, session
import os
from routes.auth import auth_bp
from routes.problems import problems_bp
from routes.submissions import submissions_bp
from routes.contests import contests_bp
from routes.users import users_bp
from routes.hacks import hacks_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(problems_bp)
app.register_blueprint(submissions_bp)
app.register_blueprint(contests_bp)
app.register_blueprint(users_bp)
app.register_blueprint(hacks_bp)

# 基础页面路由
@app.route('/')
def index():
    """首页"""
    from flask import render_template
    return render_template('index.html')

@app.route('/problems')
def problems():
    """题目列表页面"""
    from flask import render_template
    return render_template('problems.html')

@app.route('/contests')
def contests():
    """比赛列表页面"""
    from flask import render_template
    return render_template('contests.html')

@app.route('/submissions')
def submissions():
    """提交记录页面"""
    from flask import render_template
    return render_template('submissions.html')

@app.route('/hacks')
def hacks():
    """Hack记录页面"""
    from flask import render_template
    return render_template('hacks.html')

@app.route('/hack/<int:hack_id>/submissions')
def hack_submissions(hack_id):
    """某个Hack的提交详情页面"""
    from flask import render_template
    return render_template('hack_submissions.html', hack_id=hack_id)

@app.route('/users')
def users():
    """用户列表页面"""
    from flask import render_template
    return render_template('users.html')

@app.route('/profile')
def profile():
    """用户个人资料页面"""
    from flask import render_template
    return render_template('profile.html')

@app.route('/problem/<problem_id>')
def problem_detail(problem_id):
    """题目详情页面"""
    from flask import render_template
    return render_template('problem_detail.html',
                         problem={'title': '加载中...', 'difficulty': '简单'},
                         difficulty_color='secondary')

@app.route('/create-problem')
def create_problem_page():
    """题目创建页面"""
    from flask import render_template
    return render_template('create_problem.html')

@app.route('/create-contest')
def create_contest_page():
    """比赛创建页面"""
    from flask import render_template
    return render_template('create_contest.html')

@app.route('/contest/<contest_id>')
def contest_detail(contest_id):
    """比赛详情页面"""
    from flask import render_template
    return render_template('contest_detail.html', contest_id=contest_id)

@app.route('/contest/<contest_id>/standings')
def contest_standings_page(contest_id):
    """比赛排名页面"""
    from flask import render_template
    return render_template('contest_standings.html', contest_id=contest_id)

if __name__ == '__main__':
    # 使用HTTPS运行应用
    ssl_context = ('cert.pem', 'key.pem')  # 证书和密钥文件
    app.run(debug=True, host='0.0.0.0', port=8443, ssl_context=ssl_context)