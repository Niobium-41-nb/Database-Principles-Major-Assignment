function getVerdictClass(verdict) {
    switch(verdict) {
        case 'Accepted':
            return 'verdict-accepted';
        case 'Wrong Answer':
        case 'Presentation Error':
            return 'verdict-wrong';
        case 'Time Limit Exceeded':
        case 'Idleness Limit Exceeded':
            return 'verdict-time-limit';
        case 'Memory Limit Exceeded':
            return 'verdict-memory-limit';
        case 'Runtime Error':
            return 'verdict-runtime';
        case 'Compilation Error':
            return 'verdict-compilation';
        default:
            return 'verdict-other';
    }
}

async function loadSubmissions() {
    try {
        const userFilter = document.getElementById('user-filter').value;
        const problemFilter = document.getElementById('problem-filter').value;
        const verdictFilter = document.getElementById('verdict-filter').value;
        
        let url = '/api/submissions';
        const params = new URLSearchParams();
        
        if (userFilter) params.append('user_handle', userFilter);
        if (problemFilter) params.append('problem_title', problemFilter);
        if (verdictFilter) params.append('verdict', verdictFilter);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        const response = await fetch(url);
        const result = await response.json();
        
        if (result.success) {
            const tbody = document.getElementById('submissions-table-body');
            tbody.innerHTML = '';
            
            if (result.submissions.length === 0) {
                const row = document.createElement('tr');
                row.innerHTML = `<td colspan="9" style="text-align: center;">暂无提交记录</td>`;
                tbody.appendChild(row);
                return;
            }
            
                result.submissions.forEach(submission => {
                    const verdictClass = getVerdictClass(submission.verdict);
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${submission.submission_id}</td>
                        <td>${submission.handle}</td>
                        <td>${submission.problem_title}</td>
                        <td>${submission.language}</td>
                        <td class="${verdictClass}">${submission.verdict}</td>
                        <td>${submission.time_consumed}ms</td>
                        <td>${Math.floor(submission.memory_consumed / 1024)}MB</td>
                        <td>${submission.passed_tests || 0}</td>
                        <td>${submission.submission_time}</td>
                        <td>
                            <a href="/submission/${submission.submission_id}" class="btn">详情</a>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
        } else {
            alert('加载提交记录失败: ' + result.message);
        }
    } catch (error) {
        alert('加载提交记录时发生错误: ' + error.message);
    }
}

// 页面加载时获取提交记录
document.addEventListener('DOMContentLoaded', loadSubmissions);