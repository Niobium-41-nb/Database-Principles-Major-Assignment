// 加载问题列表
async function loadProblems() {
    try {
        const response = await fetch('/api/problems');
        const result = await response.json();

        if (result.success) {
            const tbody = document.getElementById('problems-table-body');
            if (!tbody) return;
            
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

// 检查管理员权限
function checkAdminPermission() {
    const createProblemBtn = document.getElementById('create-problem-btn');
    if (!createProblemBtn) return;

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

// 页面加载时执行
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('problems-table-body')) {
        loadProblems();
        checkAdminPermission();
    }
});