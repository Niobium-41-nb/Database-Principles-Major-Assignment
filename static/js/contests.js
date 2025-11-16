// static/js/contests.js - 比赛页面专用功能

let contests = [];
let currentPage = 1;
const pageSize = 20;
let filters = {
    phase: '',
    type: '',
    difficulty: '',
    search: ''
};

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

function getDifficultyClass(difficulty) {
    if (!difficulty) return '';
    if (difficulty === '简单' || difficulty === 'Easy') return 'difficulty-easy';
    if (difficulty === '中等' || difficulty === 'Medium') return 'difficulty-medium';
    if (difficulty === '困难' || difficulty === 'Hard') return 'difficulty-hard';
    return '';
}

function formatDateTime(datetimeStr) {
    if (!datetimeStr) return '-';
    const date = new Date(datetimeStr);
    return date.toLocaleString('zh-CN');
}

async function loadContests() {
    try {
        const params = new URLSearchParams({
            page: currentPage,
            page_size: pageSize,
            ...filters
        });

        const response = await fetch(`/api/contests?${params}`);
        const result = await response.json();

        if (result.success) {
            contests = result.contests;
            displayContests(contests);
            setupPagination(result.total_count);
        } else {
            console.error('加载比赛列表失败:', result.message);
            displayContests([]);
        }
    } catch (error) {
        console.error('加载比赛列表时发生错误:', error);
        displayContests([]);
    }
}

function displayContests(contests) {
    const tbody = document.getElementById('contests-table-body');

    if (!contests || contests.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-state">
                    暂无比赛数据
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = '';
    contests.forEach(contest => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${contest.contest_id}</td>
            <td>
                <a href="/contest/${contest.contest_id}" class="contest-link">
                    ${contest.name}
                </a>
            </td>
            <td class="${getPhaseClass(contest.phase)}">${getPhaseText(contest.phase)}</td>
            <td>${getTypeText(contest.type)}</td>
            <td class="${getDifficultyClass(contest.difficulty)}">${contest.difficulty || '-'}</td>
            <td>${formatDateTime(contest.start_time)}</td>
            <td>${formatDateTime(contest.end_time)}</td>
            <td>
                <a href="/contest/${contest.contest_id}" class="btn">查看</a>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function setupPagination(totalCount) {
    const totalPages = Math.ceil(totalCount / pageSize);
    const pagination = document.getElementById('pagination');

    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }

    let paginationHTML = '';

    // 上一页按钮
    if (currentPage > 1) {
        paginationHTML += `<button class="page-btn" onclick="changePage(${currentPage - 1})">上一页</button>`;
    }

    // 页码按钮
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    if (startPage > 1) {
        paginationHTML += `<button class="page-btn" onclick="changePage(1)">1</button>`;
        if (startPage > 2) {
            paginationHTML += `<span style="padding: 0.5rem;">...</span>`;
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">${i}</button>`;
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHTML += `<span style="padding: 0.5rem;">...</span>`;
        }
        paginationHTML += `<button class="page-btn" onclick="changePage(${totalPages})">${totalPages}</button>`;
    }

    // 下一页按钮
    if (currentPage < totalPages) {
        paginationHTML += `<button class="page-btn" onclick="changePage(${currentPage + 1})">下一页</button>`;
    }

    pagination.innerHTML = paginationHTML;
}

function changePage(page) {
    currentPage = page;
    loadContests();
    // 滚动到顶部
    window.scrollTo(0, 0);
}

function applyFilters() {
    filters = {
        phase: document.getElementById('phase-filter').value,
        type: document.getElementById('type-filter').value,
        difficulty: document.getElementById('difficulty-filter').value,
        search: document.getElementById('search-input').value.trim()
    };
    currentPage = 1;
    loadContests();
}

function resetFilters() {
    document.getElementById('phase-filter').value = '';
    document.getElementById('type-filter').value = '';
    document.getElementById('difficulty-filter').value = '';
    document.getElementById('search-input').value = '';
    applyFilters();
}

// 检查管理员权限
async function checkAdminPermission() {
    try {
        const response = await fetch('/api/user/current');
        const result = await response.json();

        if (result.success && result.user && result.user.is_admin) {
            document.getElementById('create-contest-btn').style.display = 'inline-block';
            document.getElementById('admin-actions').style.display = 'block';
        }
    } catch (error) {
        console.error('检查管理员权限失败:', error);
    }
}

// 创建比赛
async function createContest(contestData) {
    try {
        const response = await fetch('/api/contest/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(contestData)
        });

        const result = await response.json();

        if (result.success) {
            showMessage('比赛创建成功！', 'success');
            hideCreateContestModal();
            loadContests(); // 刷新列表
        } else {
            showMessage('创建比赛失败: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('创建比赛失败:', error);
        showMessage('创建比赛失败，请检查网络连接', 'error');
    }
}

function showCreateContestModal() {
    document.getElementById('create-contest-modal').style.display = 'block';
}

function hideCreateContestModal() {
    document.getElementById('create-contest-modal').style.display = 'none';
    document.getElementById('create-contest-form').reset();
}

// 从外部API刷新比赛数据
async function refreshContestsFromAPI() {
    try {
        const response = await fetch('/api/contests/refresh', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        if (result.success) {
            showMessage('比赛数据刷新成功！', 'success');
            loadContests(); // 刷新列表
        } else {
            showMessage('刷新比赛数据失败: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('刷新比赛数据失败:', error);
        showMessage('刷新比赛数据失败，请检查网络连接', 'error');
    }
}

// 页面加载时执行
document.addEventListener('DOMContentLoaded', function() {
    loadContests();
    checkAdminPermission();
});

// 事件监听器
document.getElementById('apply-filters-btn').addEventListener('click', applyFilters);
document.getElementById('reset-filters-btn').addEventListener('click', resetFilters);
document.getElementById('create-contest-btn').addEventListener('click', showCreateContestModal);
document.getElementById('cancel-create-btn').addEventListener('click', hideCreateContestModal);
document.getElementById('refresh-contests-btn').addEventListener('click', function() {
    if (confirm('确定要从外部API同步比赛数据吗？')) {
        refreshContestsFromAPI();
    }
});

// 创建比赛表单提交
document.getElementById('create-contest-form').addEventListener('submit', function(e) {
    e.preventDefault();

    const contestData = {
        name: document.getElementById('contest-name').value,
        description: document.getElementById('contest-description').value,
        start_time: document.getElementById('contest-start-time').value,
        end_time: document.getElementById('contest-end-time').value,
        type: document.getElementById('contest-type').value,
        difficulty: document.getElementById('contest-difficulty').value || null,
        kind: document.getElementById('contest-kind').value || null
    };

    createContest(contestData);
});