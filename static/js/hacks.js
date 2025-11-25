function getStatusClass(verdict) {
    switch(verdict.toUpperCase()) {
        case 'SUCCESSFUL':
            return 'status-successful';
        case 'UNSUCCESSFUL':
            return 'status-unsuccessful';
        default:
            return 'status-invalid';
    }
}

function formatVerdictText(verdict) {
    switch(verdict.toUpperCase()) {
        case 'SUCCESSFUL':
            return '成功';
        case 'UNSUCCESSFUL':
            return '失败';
        default:
            return '无效';
    }
}

function renderHacks(hacks) {
    const tbody = document.getElementById('hack-list');
    tbody.innerHTML = '';

    if (hacks.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td colspan="8" class="empty-state">
                暂无Hack记录
            </td>
        `;
        tbody.appendChild(tr);
        return;
    }

    hacks.forEach(hack => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>#${hack.hack_id}</td>
            <td><a href="/users/${hack.hacker}" class="user-link">${hack.hacker}</a></td>
            <td><a href="/users/${hack.defender}" class="user-link">${hack.defender}</a></td>
            <td><a href="/problem/${hack.problem_id}" class="problem-link">问题 ${hack.problem_id}</a></td>
            <td>${hack.contest_id ? `<a href="/contest/${hack.contest_id}" class="problem-link">比赛 ${hack.contest_id}</a>` : '-'}</td>
            <td><span class="hack-status ${getStatusClass(hack.verdict)}">${formatVerdictText(hack.verdict)}</span></td>
            <td><span class="timestamp">${hack.hack_time}</span></td>
            <td><a href="/hack/${hack.hack_id}/submissions" class="action-link">查看提交</a></td>
        `;
        tbody.appendChild(tr);
    });
}

let allHacks = [];

function filterHacks() {
    const verdictFilter = document.getElementById('verdict-filter').value;

    let filteredHacks = [...allHacks];

    if (verdictFilter) {
        filteredHacks = filteredHacks.filter(hack =>
            hack.verdict.toUpperCase() === verdictFilter
        );
    }

    renderHacks(filteredHacks);
}

// 添加筛选器事件监听
document.getElementById('verdict-filter').addEventListener('change', filterHacks);

// 获取数据并初始化表格
fetch('/api/hacks').then(res => res.json()).then(data => {
    if(data.success) {
        allHacks = data.hacks;
        renderHacks(allHacks);
    }
});