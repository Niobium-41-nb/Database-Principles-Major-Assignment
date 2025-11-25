// 从URL路径中获取比赛ID
function getContestId() {
    const pathParts = window.location.pathname.split('/').filter(part => part);
    // URL格式可能是 /contest/123 或 /contest/123/
    for (let i = 0; i < pathParts.length; i++) {
        if (pathParts[i] === 'contest' && i + 1 < pathParts.length) {
            const contestId = pathParts[i + 1];
            // 验证contestId是否为数字
            if (contestId && contestId.match(/^\d+$/)) {
                return contestId;
            }
        }
    }
    return null;
}

let contestId = getContestId();
let contest = null;
let countdownInterval = null;

function getPhaseText(phase) {
    const phaseMap = {
        'BEFORE': '未开始',
        'CODING': '进行中',
        'PENDING_SYSTEM_TEST': '等待系统测试',
        'SYSTEM_TEST': '系统测试中',
        'FINISHED': '已结束'
    };
    return phaseMap[phase] || phase;
}

function getPhaseClass(phase) {
    const phaseClassMap = {
        'BEFORE': 'phase-before',
        'CODING': 'phase-coding',
        'FINISHED': 'phase-finished'
    };
    return phaseClassMap[phase] || '';
}

function getTypeText(type) {
    const typeMap = {
        'CF': 'Codeforces式',
        'IOI': 'IOI式',
        'ICPC': 'ICPC式'
    };
    return typeMap[type] || type;
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}小时${minutes}分钟`;
}

function getDifficultyClass(difficulty) {
    if (!difficulty) return 'difficulty-easy';
    if (difficulty === '简单' || difficulty === 'Easy') return 'difficulty-easy';
    if (difficulty === '中等' || difficulty === 'Medium') return 'difficulty-medium';
    if (difficulty === '困难' || difficulty === 'Hard') return 'difficulty-hard';
    return 'difficulty-easy';
}

function updateCountdown(endTime) {
    const end = new Date(endTime).getTime();
    const now = new Date().getTime();
    const distance = end - now;

    if (distance < 0) {
        document.getElementById('countdown').style.display = 'none';
        if (countdownInterval) {
            clearInterval(countdownInterval);
        }
        return;
    }

    const hours = Math.floor(distance / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    document.getElementById('countdown-timer').textContent =
        `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

async function loadContestDetail() {
    if (!contestId) {
        showError('比赛ID不存在或格式错误');
        return;
    }

    try {
        const response = await fetch(`/api/contest/${contestId}`);
        const result = await response.json();

        if (result.success) {
            contest = result.contest;
            displayContestDetail(contest);
            loadContestProblems();
        } else {
            showError(result.message);
        }
    } catch (error) {
        showError('加载比赛详情失败: ' + error.message);
    }
}

function displayContestDetail(contest) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('contest-content').style.display = 'block';

    // 更新标题
    document.getElementById('contest-title').textContent = contest.name;
    document.title = `${contest.name} - 在线判题系统`;

    // 更新排名链接
    document.getElementById('standings-link').href = `/contest/${contest.contest_id}/standings`;

    // 更新比赛信息
    const contestMeta = document.getElementById('contest-meta');
    contestMeta.innerHTML = `
        <div class="meta-item">
            <span class="meta-label">比赛阶段</span>
            <span class="meta-value ${getPhaseClass(contest.phase)}">${getPhaseText(contest.phase)}</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">比赛类型</span>
            <span class="meta-value">${getTypeText(contest.type)}</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">开始时间</span>
            <span class="meta-value">${contest.start_time}</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">结束时间</span>
            <span class="meta-value">${contest.end_time}</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">持续时间</span>
            <span class="meta-value">${formatDuration(contest.duration)}</span>
        </div>
        ${contest.difficulty ? `
        <div class="meta-item">
            <span class="meta-label">难度评级</span>
            <span class="meta-value">${contest.difficulty}</span>
        </div>
        ` : ''}
        ${contest.kind ? `
        <div class="meta-item">
            <span class="meta-label">比赛种类</span>
            <span class="meta-value">${contest.kind}</span>
        </div>
        ` : ''}
        ${contest.icpc_region ? `
        <div class="meta-item">
            <span class="meta-label">区域</span>
            <span class="meta-value">${contest.icpc_region}</span>
        </div>
        ` : ''}
        ${contest.country ? `
        <div class="meta-item">
            <span class="meta-label">国家</span>
            <span class="meta-value">${contest.country}</span>
        </div>
        ` : ''}
        ${contest.city ? `
        <div class="meta-item">
            <span class="meta-label">城市</span>
            <span class="meta-value">${contest.city}</span>
        </div>
        ` : ''}
    `;

    // 更新比赛描述
    const descriptionContainer = document.getElementById('contest-description');
    if (contest.description && contest.description.trim() !== '') {
        descriptionContainer.innerHTML = `
            <h3 class="section-title">比赛描述</h3>
            <div class="description-content">${contest.description}</div>
        `;
    } else {
        descriptionContainer.innerHTML = '';
    }

    // 设置按钮状态和倒计时
    if (contest.phase === 'CODING') {
        document.getElementById('countdown').style.display = 'block';
        document.getElementById('enter-btn').style.display = 'inline-block';
        // 立即更新一次倒计时
        updateCountdown(contest.end_time);
        // 设置定时器每秒更新
        countdownInterval = setInterval(() => updateCountdown(contest.end_time), 1000);
    } else if (contest.phase === 'BEFORE') {
        document.getElementById('register-btn').style.display = 'inline-block';
    }
}

async function loadContestProblems() {
    try {
        const response = await fetch(`/api/contest/${contestId}/problems`);
        const result = await response.json();

        if (result.success) {
            displayContestProblems(result.problems);
        } else {
            console.error('加载比赛题目失败:', result.message);
            displayContestProblems([]);
        }
    } catch (error) {
        console.error('加载比赛题目时发生错误:', error);
        displayContestProblems([]);
    }
}

function displayContestProblems(problems) {
    const tbody = document.getElementById('problems-table-body');

    if (!problems || problems.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    暂无题目数据
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = '';
    problems.forEach(problem => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${problem.problem_id || 'N/A'}</td>
            <td>
                <a href="/problem/${problem.problem_id}" class="problem-link">
                    ${problem.title || '未知题目'}
                </a>
            </td>
            <td class="${getDifficultyClass(problem.difficulty)}">
                ${problem.difficulty || '简单'}
            </td>
            <td>${problem.time_limit || 1000}ms</td>
            <td>${problem.memory_limit ? Math.floor(problem.memory_limit / 1024) : 256}MB</td>
        `;
        tbody.appendChild(row);
    });
}

function showError(message) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('contest-content').style.display = 'none';
    document.getElementById('error-message').style.display = 'block';
    document.getElementById('error-text').textContent = message;

    // 清理定时器
    if (countdownInterval) {
        clearInterval(countdownInterval);
    }
}

// 检查管理员权限并显示管理面板
async function checkAdminPermission() {
    try {
        const response = await fetch('/api/user/current');
        const result = await response.json();

        if (result.success && result.user && result.user.is_admin) {
            document.getElementById('admin-panel').style.display = 'block';
            loadAvailableProblems();
        }
    } catch (error) {
        console.error('检查管理员权限失败:', error);
    }
}

// 加载可用的题目列表
async function loadAvailableProblems() {
    try {
        const response = await fetch(`/api/contest/${contestId}/available_problems`);
        const result = await response.json();

        if (result.success) {
            displayAvailableProblems(result.problems);
        } else {
            console.error('加载可用题目失败:', result.message);
            displayAvailableProblems([]);
            document.getElementById('admin-problems-table-body').innerHTML = `
                <tr>
                    <td colspan="5" class="empty-state">
                        加载题目失败: ${result.message}
                    </td>
                </tr>
            `;
        }
    } catch (error) {
        console.error('加载可用题目时发生错误:', error);
        displayAvailableProblems([]);
        document.getElementById('admin-problems-table-body').innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    加载题目时发生错误
                </td>
            </tr>
        `;
    }
}

// 显示可用的题目列表
function displayAvailableProblems(problems) {
    const select = document.getElementById('problem-select');
    select.innerHTML = '<option value="">请选择题目</option>';

    problems.forEach(problem => {
        const option = document.createElement('option');
        option.value = problem.problem_id;
        option.textContent = `${problem.problem_id} - ${problem.title} (${problem.difficulty})`;
        option.disabled = problem.in_contest; // 已在比赛中的题目禁用
        if (problem.in_contest) {
            option.textContent += ' [已在比赛中]';
        }
        select.appendChild(option);
    });

    // 更新管理员视角的题目列表
    const adminTbody = document.getElementById('admin-problems-table-body');
    const contestProblems = problems.filter(p => p.in_contest);

    if (contestProblems.length === 0) {
        adminTbody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    暂无题目，请添加题目到比赛
                </td>
            </tr>
        `;
        return;
    }

    adminTbody.innerHTML = '';
    contestProblems.forEach(problem => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${problem.problem_index || 'A'}</td>
            <td>${problem.problem_id}</td>
            <td>
                <a href="/problem/${problem.problem_id}" class="problem-link">
                    ${problem.title}
                </a>
            </td>
            <td class="${getDifficultyClass(problem.difficulty)}">
                ${problem.difficulty || '简单'}
            </td>
            <td>
                <button class="btn btn-danger" onclick="removeProblemFromContest('${problem.problem_id}')">
                    移除
                </button>
            </td>
        `;
        adminTbody.appendChild(row);
    });
}

// 添加题目到比赛
async function addProblemToContest() {
    const problemId = document.getElementById('problem-select').value;
    const problemIndex = document.getElementById('problem-index').value.trim();

    if (!problemId) {
        alert('请选择题目');
        return;
    }

    if (!problemIndex) {
        alert('请输入题目索引');
        return;
    }

    try {
        const response = await fetch(`/api/contest/${contestId}/add_problem`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                problem_id: problemId,
                problem_index: problemIndex
            })
        });

        const result = await response.json();

        if (result.success) {
            alert('题目添加成功');
            // 刷新题目列表
            loadAvailableProblems();
            loadContestProblems(); // 刷新普通用户看到的题目列表
            // 隐藏添加表单
            document.getElementById('add-problem-form').style.display = 'none';
            // 重置表单
            document.getElementById('problem-select').value = '';
            document.getElementById('problem-index').value = 'A';
        } else {
            alert('添加题目失败: ' + result.message);
        }
    } catch (error) {
        console.error('添加题目失败:', error);
        alert('添加题目失败，请检查网络连接');
    }
}

// 从比赛中移除题目
async function removeProblemFromContest(problemId) {
    if (!confirm('确定要从比赛中移除这个题目吗？')) {
        return;
    }

    try {
        const response = await fetch(`/api/contest/${contestId}/remove_problem`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                problem_id: problemId
            })
        });

        const result = await response.json();

        if (result.success) {
            alert('题目移除成功');
            // 刷新题目列表
            loadAvailableProblems();
            loadContestProblems(); // 刷新普通用户看到的题目列表
        } else {
            alert('移除题目失败: ' + result.message);
        }
    } catch (error) {
        console.error('移除题目失败:', error);
        alert('移除题目失败，请检查网络连接');
    }
}

// 报名参赛
document.getElementById('register-btn').addEventListener('click', function() {
    if (confirm('确定要报名参加这个比赛吗？')) {
        registerForContest();
    }
});

// 进入比赛
document.getElementById('enter-btn').addEventListener('click', function() {
    // 对于进行中的比赛，进入比赛就是刷新页面查看最新状态
    location.reload();
});

// 报名参赛的API调用
async function registerForContest() {
    try {
        // 这里调用报名API
        const response = await fetch(`/api/contest/${contestId}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();
            if (result.success) {
                alert('报名成功！');
                document.getElementById('register-btn').disabled = true;
                document.getElementById('register-btn').textContent = '已报名';
            } else {
                alert('报名失败: ' + result.message);
            }
        } else {
            alert('报名失败，请稍后重试');
        }
    } catch (error) {
        console.error('报名失败:', error);
        alert('报名失败，请检查网络连接');
    }
}

// 检查用户登录状态
async function checkLoginStatus() {
    try {
        const response = await fetch('/api/user/current');
        const result = await response.json();

        if (!result.success) {
            // 用户未登录，隐藏报名和进入按钮
            document.getElementById('register-btn').style.display = 'none';
            document.getElementById('enter-btn').style.display = 'none';
        }
    } catch (error) {
        console.error('检查登录状态失败:', error);
    }
}

// 页面加载时执行
document.addEventListener('DOMContentLoaded', function() {
    checkLoginStatus();
    loadContestDetail();
    checkAdminPermission();
});

// 页面卸载时清理定时器
window.addEventListener('beforeunload', function() {
    if (countdownInterval) {
        clearInterval(countdownInterval);
    }
});

// 添加事件监听器
document.getElementById('manage-problems-btn').addEventListener('click', function() {
    const form = document.getElementById('add-problem-form');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
});

document.getElementById('refresh-problems-btn').addEventListener('click', function() {
    loadAvailableProblems();
});

document.getElementById('add-problem-btn').addEventListener('click', addProblemToContest);

document.getElementById('cancel-add-btn').addEventListener('click', function() {
    document.getElementById('add-problem-form').style.display = 'none';
    document.getElementById('problem-select').value = '';
    document.getElementById('problem-index').value = 'A';
});

// 生成排名
document.getElementById('generate-standings-btn').addEventListener('click', async function() {
    if (!confirm('确定要生成比赛排名吗？这将根据提交记录重新计算排名。')) {
        return;
    }

    try {
        const response = await fetch(`/api/contest/${contestId}/generate_standings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        if (result.success) {
            alert('排名生成成功！');
            // 刷新排名页面
            window.location.href = `/contest/${contestId}/standings`;
        } else {
            alert('生成排名失败: ' + result.message);
        }
    } catch (error) {
        console.error('生成排名失败:', error);
        alert('生成排名失败，请检查网络连接');
    }
});