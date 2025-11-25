// static/js/common.js - 公共JavaScript功能

// 登录相关功能
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

// 登录功能
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

// 注册功能
async function register() {
    const handle = document.getElementById('register-handle').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const name = document.getElementById('register-name').value;
    
    if (!handle || !email || !password) {
        alert('请填写必填信息');
        return;
    }
    
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ handle, email, password, name })
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

// 检查登录状态
function checkLoginStatus() {
    const userInfo = document.getElementById('user-info');
    const guestButtons = document.getElementById('guest-buttons');
    const userHandle = document.getElementById('user-handle');
    const profileLink = document.getElementById('profile-link');
    
    if (!userInfo || !guestButtons) return;
    
    fetch('/api/user/current')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.user) {
                userHandle.textContent = data.user.handle;
                userInfo.style.display = 'block';
                guestButtons.style.display = 'none';
                
                // 更新个人资料链接
                if (profileLink) {
                    profileLink.textContent = data.user.handle;
                }
            } else {
                userInfo.style.display = 'none';
                guestButtons.style.display = 'block';
                
                // 重置个人资料链接
                if (profileLink) {
                    profileLink.textContent = '个人资料';
                }
            }
        })
        .catch(() => {
            userInfo.style.display = 'none';
            guestButtons.style.display = 'block';
        });
}

// 检查管理员权限
function checkAdminStatus() {
    const createProblemBtn = document.getElementById('create-problem-btn');
    const createContestBtn = document.getElementById('create-contest-btn');
    
    if (!createProblemBtn && !createContestBtn) return;
    
    fetch('/api/user/current')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.user && data.user.is_admin) {
                // 只有管理员才显示创建按钮
                if (createProblemBtn) createProblemBtn.style.display = 'inline-block';
                if (createContestBtn) createContestBtn.style.display = 'inline-block';
            } else {
                if (createProblemBtn) createProblemBtn.style.display = 'none';
                if (createContestBtn) createContestBtn.style.display = 'none';
            }
        })
        .catch(() => {
            if (createProblemBtn) createProblemBtn.style.display = 'none';
            if (createContestBtn) createContestBtn.style.display = 'none';
        });
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

// 格式化时间
function formatTime(timestamp) {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// 格式化内存大小
function formatMemory(bytes) {
    if (bytes < 1024) return bytes + 'B';
    if (bytes < 1024 * 1024) return Math.floor(bytes / 1024) + 'KB';
    return Math.floor(bytes / (1024 * 1024)) + 'MB';
}

// 显示消息
function showMessage(message, type = 'info') {
    // 创建消息元素
    const messageEl = document.createElement('div');
    messageEl.className = `message message-${type}`;
    messageEl.textContent = message;
    messageEl.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem;
        border-radius: 4px;
        color: white;
        z-index: 10000;
        max-width: 300px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;
    
    // 设置颜色
    const colors = {
        info: '#3498db',
        success: '#27ae60',
        warning: '#f39c12',
        error: '#e74c3c'
    };
    messageEl.style.background = colors[type] || colors.info;
    
    // 添加到页面
    document.body.appendChild(messageEl);
    
    // 3秒后自动移除
    setTimeout(() => {
        messageEl.style.opacity = '0';
        messageEl.style.transition = 'opacity 0.5s';
        setTimeout(() => {
            if (messageEl.parentNode) {
                messageEl.parentNode.removeChild(messageEl);
            }
        }, 500);
    }, 3000);
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    checkLoginStatus();
    checkAdminStatus();
    
    // 添加模态框点击外部关闭功能
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
            }
        });
    });
});