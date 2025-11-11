// 检查登录状态
function checkLoginStatus() {
    const createProblemBtn = document.getElementById('create-problem-btn');

    fetch('/api/user/current')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.user && data.user.is_admin) {
                // 只有管理员才显示创建题目按钮
                createProblemBtn.style.display = 'inline-block';
            } else {
                createProblemBtn.style.display = 'none';
            }
        })
        .catch(() => {
            createProblemBtn.style.display = 'none';
        });
}

// 登录相关函数
function showLogin() {
    document.getElementById('login-modal').style.display = 'block';
}

function hideLogin() {
    document.getElementById('login-modal').style.display = 'none';
}

function showRegister() {
    document.getElementById('register-modal').style.display = 'block';
}

function hideRegister() {
    document.getElementById('register-modal').style.display = 'none';
}

async function login() {
    const handle = document.getElementById('login-handle').value;
    const password = document.getElementById('login-password').value;

    if (!handle || !password) {
        alert('请填写用户名和密码');
        return;
    }

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ handle, password })
        });

        const result = await response.json();
        alert(result.message);
        if (result.success) {
            hideLogin();
            location.reload();
        }
    } catch (error) {
        alert('登录失败: ' + error.message);
    }
}

async function register() {
    const handle = document.getElementById('register-handle').value;
    const email = document.getElementById('register-email').value;
    const name = document.getElementById('register-name').value;
    const password = document.getElementById('register-password').value;

    if (!handle || !email || !password) {
        alert('请填写必填信息');
        return;
    }

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ handle, email, name, password })
        });

        const result = await response.json();
        alert(result.message);
        if (result.success) {
            hideRegister();
            // 注册成功后自动登录
            const loginResponse = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ handle, password })
            });

            const loginResult = await loginResponse.json();
            if (loginResult.success) {
                location.reload();
            }
        }
    } catch (error) {
        alert('注册失败: ' + error.message);
    }
}

// 登出功能
async function logout() {
    try {
        const response = await fetch('/api/logout');
        const result = await response.json();
        alert(result.message);
        if (result.success) {
            location.reload();
        }
    } catch (error) {
        alert('登出失败: ' + error.message);
    }
}

async function loadProblems() {
    try {
        const response = await fetch('/api/problems');
        const result = await response.json();

        if (result.success) {
            const tbody = document.getElementById('problems-table-body');
            tbody.innerHTML = '';

            result.problems.forEach(problem => {
                const passRate = problem.submission_count > 0
                    ? ((problem.accepted_count / problem.submission_count) * 100).toFixed(1) + '%'
                    : '0%';

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${problem.problem_id}</td>
                    <td>
                        <a href="/problem/${problem.problem_id}" class="problem-link">
                            ${problem.title}
                        </a>
                    </td>
                    <td class="difficulty-${getDifficultyClass(problem.difficulty)}">
                        ${problem.difficulty || '简单'}
                    </td>
                    <td>${problem.accepted_count}/${problem.submission_count} (${passRate})</td>
                    <td>${problem.time_limit}ms</td>
                    <td>${Math.floor(problem.memory_limit / 1024)}MB</td>
                `;
                tbody.appendChild(row);
            });
        } else {
            alert('加载题目失败: ' + result.message);
        }
    } catch (error) {
        alert('加载题目时发生错误: ' + error.message);
    }
}

// 辅助函数：根据难度返回对应的CSS类名
function getDifficultyClass(difficulty) {
    if (!difficulty) return 'easy';

    const difficultyMap = {
        '简单': 'easy',
        '中等': 'medium',
        '困难': 'hard',
        'Easy': 'easy',
        'Medium': 'medium',
        'Hard': 'hard'
    };

    return difficultyMap[difficulty] || 'easy';
}

// 页面加载时执行
document.addEventListener('DOMContentLoaded', function() {
    checkLoginStatus();
    loadProblems();
});