// static/js/problems.js - 题目页面专用功能

// 加载题目列表
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
            showMessage('加载题目失败: ' + result.message, 'error');
        }
    } catch (error) {
        showMessage('加载题目时发生错误: ' + error.message, 'error');
    }
}

// 页面加载时执行
document.addEventListener('DOMContentLoaded', function() {
    loadProblems();
});