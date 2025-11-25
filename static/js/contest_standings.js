// 从URL路径中获取比赛ID
function getContestId() {
    const pathParts = window.location.pathname.split('/').filter(part => part);
    // URL格式可能是 /contest/123/standings 或 /contest/123/standings/
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
let standings = [];
let currentPage = 1;
const pageSize = 50;

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

function getRatingClass(rating) {
    if (!rating) return 'rating-newbie';
    if (rating >= 2400) return 'rating-high';
    if (rating >= 1800) return 'rating-medium';
    if (rating >= 1200) return 'rating-low';
    return 'rating-newbie';
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}小时${minutes}分钟`;
}

function formatPenalty(penalty) {
    if (!penalty) return '0';
    const minutes = Math.floor(penalty / 60);
    return `${minutes}`;
}

function formatRatingChange(ratingChange) {
    if (ratingChange === null || ratingChange === undefined) return '-';
    if (ratingChange > 0) return `<span class="rating-positive">+${ratingChange}</span>`;
    if (ratingChange < 0) return `<span class="rating-negative">${ratingChange}</span>`;
    return '<span class="rating-zero">0</span>';
}

async function loadContestInfo() {
    if (!contestId) {
        showError('比赛ID不存在或格式错误');
        return;
    }

    try {
        const response = await fetch(`/api/contest/${contestId}`);
        const result = await response.json();

        if (result.success) {
            contest = result.contest;
            displayContestInfo(contest);
        } else {
            showError(result.message);
        }
    } catch (error) {
        showError('加载比赛信息失败: ' + error.message);
    }
}

function displayContestInfo(contest) {
    document.getElementById('contest-title').textContent = `${contest.name} - 排名`;
    document.title = `${contest.name} - 排名 - 在线判题系统`;

    // 更新返回链接
    document.getElementById('contest-detail-link').href = `/contest/${contest.contest_id}`;

    const contestInfo = document.getElementById('contest-info');
    contestInfo.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
            <div>
                <strong>比赛阶段:</strong>
                <span class="contest-phase ${getPhaseClass(contest.phase)}">${getPhaseText(contest.phase)}</span>
            </div>
            <div><strong>开始时间:</strong> ${contest.start_time}</div>
            <div><strong>结束时间:</strong> ${contest.end_time}</div>
            <div><strong>持续时间:</strong> ${formatDuration(contest.duration)}</div>
        </div>
    `;
}

async function loadStandings() {
    try {
        const response = await fetch(`/api/contest/${contestId}/standings?page=${currentPage}&page_size=${pageSize}`);
        const result = await response.json();

        if (result.success) {
            standings = result.standings;
            displayStandings(standings);
            setupPagination(result.total_count);
        } else {
            showError(result.message);
        }
    } catch (error) {
        showError('加载排名失败: ' + error.message);
    }
}

function displayStandings(standings) {
    const tbody = document.getElementById('standings-table-body');

    if (!standings || standings.length == 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 2rem; color: #666;">
                    暂无排名数据
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = '';
    standings.forEach((row, index) => {
        const rank = (currentPage - 1) * pageSize + index + 1;
        const tr = document.createElement('tr');
        if (rank <= 3) {
            tr.className = `rank-${rank}`;
        }
        
        // 修复这里：确保使用正确的字段名
        const username = row.username || row.handle || 'Unknown'; // 添加回退逻辑
        const userRating = row.rating || 0;
        const solvedCount = row.solved_count || 0;
        const penalty = row.penalty || 0;
        const totalScore = row.total_score || row.scores || 0; // 兼容两种字段名
        const ratingChange = row.rating_change;

        tr.innerHTML = `
            <td>${rank}</td>
            <td style="text-align: left;">
                <a href="/user/${row.user_id}" class="user-handle ${getRatingClass(userRating)}">
                    ${username}
                </a>
                ${row.is_me ? '<span style="color: #e74c3c; margin-left: 0.5rem;">[我]</span>' : ''}
            </td>
            <td class="${getRatingClass(userRating)}">${userRating || '-'}</td>
            <td>${solvedCount}</td>
            <td>${formatPenalty(penalty)}</td>
            <td>${totalScore}</td>
            <td>${formatRatingChange(ratingChange)}</td>
        `;
        tbody.appendChild(tr);
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
    loadStandings();
    // 滚动到顶部
    window.scrollTo(0, 0);
}

function showError(message) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('standings-content').style.display = 'none';
    document.getElementById('error-message').style.display = 'block';
    document.getElementById('error-text').textContent = message;
}

// 检查管理员权限
async function checkAdminPermission() {
    try {
        const response = await fetch('/api/user/current');
        const result = await response.json();

        if (result.success && result.user && result.user.is_admin) {
            document.getElementById('admin-actions').style.display = 'block';
        }
    } catch (error) {
        console.error('检查管理员权限失败:', error);
    }
}

// 页面加载时执行
document.addEventListener('DOMContentLoaded', function() {
    if (!contestId) {
        showError('比赛ID不存在或格式错误');
        return;
    }

    loadContestInfo();
    loadStandings();
    checkAdminPermission();

    // 隐藏加载提示，显示内容
    setTimeout(() => {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('standings-content').style.display = 'block';
    }, 500);
});

// 刷新排名
document.getElementById('refresh-standings-btn').addEventListener('click', function() {
    loadStandings();
});

// 重新生成排名（管理员功能）
document.getElementById('generate-standings-btn').addEventListener('click', async function() {
    if (!confirm('确定要重新生成排名吗？这将根据提交记录重新计算排名。')) {
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
            // 刷新排名
            loadStandings();
        } else {
            alert('生成排名失败: ' + result.message);
        }
    } catch (error) {
        console.error('生成排名失败:', error);
        alert('生成排名失败，请检查网络连接');
    }
});