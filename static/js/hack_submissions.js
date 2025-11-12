// 从DOM中获取hack_id
function getHackId() {
    const urlParts = window.location.pathname.split('/');
    for (let i = 0; i < urlParts.length; i++) {
        if (urlParts[i] === 'hack' && i + 1 < urlParts.length) {
            const hackId = urlParts[i + 1];
            if (hackId && hackId.match(/^\d+$/)) {
                return hackId;
            }
        }
    }
    return null;
}

const hackId = getHackId();

// 获取判题结果的样式类
function getVerdictClass(verdict) {
    if (!verdict) return 'verdict-failed';
    const verdictStr = String(verdict).toUpperCase();
    if (verdictStr === 'SUCCESSFUL') return 'verdict-accepted';
    return 'verdict-failed';
}

// 获取判题结果的显示文本
function getVerdictText(verdict) {
    if (!verdict) return '未知';
    const verdictStr = String(verdict).toUpperCase();
    switch (verdictStr) {
        case 'SUCCESSFUL': return 'Hack成功';
        case 'UNSUCCESSFUL': return 'Hack失败';
        case 'INVALID': return '无效Hack';
        default: return verdict;
    }
}

// 获取并渲染Hack详情
function loadHackSubmissions() {
    if (!hackId) {
        document.getElementById('submission-list').innerHTML = `
            <div class="submission-card">
                <div class="submission-body">
                    <div style="text-align: center; padding: 20px; color: #721c24;">
                        无效的Hack ID
                    </div>
                </div>
            </div>
        `;
        return;
    }

    fetch(`/api/hack/${hackId}/submissions`).then(res => res.json()).then(data => {
        if(data.success) {
            const container = document.getElementById('submission-list');

            // 更新Hack状态
            const hackStatus = document.getElementById('hack-status');
            if (data.hack_status) {
                hackStatus.textContent = getVerdictText(data.hack_status);
                hackStatus.className = `info-value ${getVerdictClass(data.hack_status)}`;
            }

            // 检查是否有提交数据
            if (!data.submission) {
                container.innerHTML = `
                    <div class="submission-card">
                        <div class="submission-body">
                            <div style="text-align: center; padding: 20px; color: #666;">
                                未找到相关提交记录
                            </div>
                        </div>
                    </div>
                `;
                return;
            }

            // 渲染单个提交记录
            const sub = data.submission;
            const submissionCard = document.createElement('div');
            submissionCard.className = 'submission-card';
            submissionCard.innerHTML = `
                <div class="submission-header">
                    <div class="submission-id">
                        提交 #${sub.submission_id}
                    </div>
                    <div class="submission-time">
                        ${sub.submission_time}
                    </div>
                </div>
                <div class="submission-body">
                    <div class="submission-detail">
                        <div class="info-label">提交者</div>
                        <div class="info-value">
                            <a href="/users/${sub.defender}" class="user-link">${sub.defender}</a>
                        </div>
                    </div>
                    <div class="submission-detail">
                        <div class="info-label">语言</div>
                        <div class="info-value">
                            <span class="language-badge">${sub.language}</span>
                        </div>
                    </div>
                    <div class="submission-detail">
                        <div class="info-label">判题结果</div>
                        <div class="info-value">
                            <span class="verdict-badge ${getVerdictClass(sub.verdict)}">${getVerdictText(sub.verdict)}</span>
                        </div>
                    </div>
                    <div class="submission-detail">
                        <div class="info-label">得分</div>
                        <div class="info-value">
                            <span class="points-badge">${sub.points || 0}</span>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(submissionCard);
        } else {
            document.getElementById('submission-list').innerHTML = `
                <div class="submission-card">
                    <div class="submission-body">
                        <div style="text-align: center; padding: 20px; color: #721c24;">
                            加载失败：${data.message || '未知错误'}
                        </div>
                    </div>
                </div>
            `;
        }
    }).catch(error => {
        document.getElementById('submission-list').innerHTML = `
            <div class="submission-card">
                <div class="submission-body">
                    <div style="text-align: center; padding: 20px; color: #721c24;">
                        加载失败：${error.message || '未知错误'}
                    </div>
                </div>
            </div>
        `;
    });
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    loadHackSubmissions();
});