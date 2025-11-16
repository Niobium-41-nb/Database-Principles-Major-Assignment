// create_contest.js - 创建比赛页面专用JavaScript

let selectedProblems = [];
let availableProblems = [];

// 加载可用的题目
async function loadAvailableProblems() {
    try {
        const response = await fetch('/api/problems');
        const result = await response.json();

        if (result.success) {
            availableProblems = result.problems;
        } else {
            alert('加载题目列表失败: ' + result.message);
        }
    } catch (error) {
        alert('加载题目列表时发生错误: ' + error.message);
    }
}

// 显示题目选择模态框
function showProblemSelectionModal() {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>选择题目</h3>
            <div class="search-box">
                <input type="text" id="problem-search" placeholder="搜索题目名称或ID..." class="auth-input">
            </div>
            <div class="problem-list" id="problem-selection-list">
                <!-- 题目列表将通过JavaScript动态加载 -->
            </div>
            <div class="modal-actions">
                <span id="selected-problems-count">已选择 0 个题目</span>
                <div>
                    <button id="confirm-selection" class="btn btn-success">确认选择</button>
                    <button id="cancel-selection" class="btn btn-secondary">取消</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    displayProblemSelectionList();

    // 事件监听器
    document.getElementById('problem-search').addEventListener('input', function(e) {
        filterProblems(e.target.value);
    });

    document.getElementById('confirm-selection').addEventListener('click', function() {
        document.body.removeChild(modal);
        updateSelectedProblemsDisplay();
    });

    document.getElementById('cancel-selection').addEventListener('click', function() {
        document.body.removeChild(modal);
    });
}

// 显示题目选择列表
function displayProblemSelectionList(filteredProblems = null) {
    const container = document.getElementById('problem-selection-list');
    const problems = filteredProblems || availableProblems;

    if (problems.length === 0) {
        container.innerHTML = '<div class="empty-state">暂无题目</div>';
        return;
    }

    container.innerHTML = '';
    problems.forEach(problem => {
        const isSelected = selectedProblems.some(p => p.problem_id === problem.problem_id);

        const problemDiv = document.createElement('div');
        problemDiv.className = `problem-option ${isSelected ? 'selected' : ''}`;
        problemDiv.innerHTML = `
            <div class="problem-header">
                <input type="checkbox" ${isSelected ? 'checked' : ''}
                       onchange="toggleProblemSelection('${problem.problem_id}', this.checked)"
                       class="problem-checkbox">
                <div class="problem-info">
                    <div class="problem-title">${problem.problem_id} - ${problem.title}</div>
                    <div class="problem-meta">
                        难度: ${problem.difficulty} | 时间限制: ${problem.time_limit}ms | 内存限制: ${Math.floor(problem.memory_limit / 1024)}MB
                    </div>
                </div>
            </div>
        `;
        container.appendChild(problemDiv);
    });

    updateSelectionCount();
}

// 过滤题目
function filterProblems(searchTerm) {
    if (!availableProblems) return;

    const filtered = availableProblems.filter(problem =>
        problem.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        problem.problem_id.toLowerCase().includes(searchTerm.toLowerCase())
    );

    displayProblemSelectionList(filtered);
}

// 切换题目选择
function toggleProblemSelection(problemId, isSelected) {
    const problem = availableProblems.find(p => p.problem_id === problemId);

    if (isSelected) {
        if (!selectedProblems.some(p => p.problem_id === problemId)) {
            selectedProblems.push({
                ...problem,
                index: String.fromCharCode(65 + selectedProblems.length) // A, B, C, ...
            });
        }
    } else {
        selectedProblems = selectedProblems.filter(p => p.problem_id !== problemId);
        // 重新分配索引
        selectedProblems.forEach((problem, index) => {
            problem.index = String.fromCharCode(65 + index);
        });
    }

    displayProblemSelectionList();
    updateSelectionCount();
}

// 更新选择计数
function updateSelectionCount() {
    const countElement = document.getElementById('selected-problems-count');
    if (countElement) {
        countElement.textContent = `已选择 ${selectedProblems.length} 个题目`;
    }
}

// 更新已选择题目的显示
function updateSelectedProblemsDisplay() {
    const container = document.getElementById('selected-problems-list');
    const countElement = document.getElementById('selected-count');

    countElement.textContent = `已选择 ${selectedProblems.length} 个题目`;

    if (selectedProblems.length === 0) {
        container.innerHTML = '<div class="empty-state">尚未选择任何题目</div>';
        return;
    }

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th width="80">索引</th>
                    <th width="120">题目ID</th>
                    <th>标题</th>
                    <th width="100">难度</th>
                    <th width="100">操作</th>
                </tr>
            </thead>
            <tbody>
                ${selectedProblems.map(problem => `
                    <tr>
                        <td>
                            <input type="text" value="${problem.index}"
                                   onchange="updateProblemIndex('${problem.problem_id}', this.value)"
                                   class="index-input">
                        </td>
                        <td>${problem.problem_id}</td>
                        <td>${problem.title}</td>
                        <td>${problem.difficulty}</td>
                        <td>
                            <button type="button" onclick="removeSelectedProblem('${problem.problem_id}')"
                                    class="btn btn-secondary small-btn">
                                移除
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// 更新题目索引
function updateProblemIndex(problemId, newIndex) {
    const problem = selectedProblems.find(p => p.problem_id === problemId);
    if (problem) {
        problem.index = newIndex;
    }
}

// 移除已选择的题目
function removeSelectedProblem(problemId) {
    selectedProblems = selectedProblems.filter(p => p.problem_id !== problemId);
    // 重新分配索引
    selectedProblems.forEach((problem, index) => {
        problem.index = String.fromCharCode(65 + index);
    });
    updateSelectedProblemsDisplay();
}

// 处理表单提交
document.getElementById('contest-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const contestData = {
        name: formData.get('name'),
        type: formData.get('type'),
        phase: formData.get('phase'),
        start_time: formData.get('start_time'),
        duration_seconds: parseInt(formData.get('duration_seconds')),
        description: formData.get('description'),
        difficulty: formData.get('difficulty') ? parseInt(formData.get('difficulty')) : 0,
        kind: formData.get('kind')
    };

    // 验证必填字段
    if (!contestData.name || !contestData.start_time || !contestData.duration_seconds) {
        alert('请填写所有必填字段');
        return;
    }

    try {
        const response = await fetch('/api/contests/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(contestData)
        });

        const result = await response.json();

        if (result.success) {
            alert('比赛创建成功！');
            // 如果有选择的题目，添加到比赛
            if (selectedProblems.length > 0) {
                await addProblemsToContest(result.contest_id);
            }
            window.location.href = `/contest/${result.contest_id}`;
        } else {
            alert('创建比赛失败: ' + result.message);
        }
    } catch (error) {
        alert('创建比赛时发生错误: ' + error.message);
    }
});

// 添加题目到新创建的比赛
async function addProblemsToContest(contestId) {
    for (const problem of selectedProblems) {
        try {
            const response = await fetch(`/api/contest/${contestId}/add_problem`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    problem_id: problem.problem_id,
                    problem_index: problem.index
                })
            });

            const result = await response.json();
            if (!result.success) {
                console.error(`添加题目 ${problem.problem_id} 失败:`, result.message);
            }
        } catch (error) {
            console.error(`添加题目 ${problem.problem_id} 时发生错误:`, error);
        }
    }
}

// 设置默认开始时间（当前时间+1小时）
function setDefaultStartTime() {
    const now = new Date();
    now.setHours(now.getHours() + 1);
    now.setMinutes(0);
    now.setSeconds(0);

    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');

    document.getElementById('start-time').value = `${year}-${month}-${day}T${hours}:${minutes}`;
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    loadAvailableProblems();
    setDefaultStartTime();
    document.getElementById('add-problem-btn').addEventListener('click', showProblemSelectionModal);
});