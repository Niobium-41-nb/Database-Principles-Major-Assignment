// 认证相关函数
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
                if (userHandle) userHandle.textContent = data.user.handle;
                if (profileLink) profileLink.style.display = 'inline';
                userInfo.style.display = 'block';
                guestButtons.style.display = 'none';
            } else {
                userInfo.style.display = 'none';
                guestButtons.style.display = 'block';
                if (profileLink) profileLink.style.display = 'none';
            }
        })
        .catch(() => {
            userInfo.style.display = 'none';
            guestButtons.style.display = 'block';
            if (profileLink) profileLink.style.display = 'none';
        });
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

// 页面加载时检查登录状态
document.addEventListener('DOMContentLoaded', function() {
    checkLoginStatus();
});

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

// 模态框点击外部关闭
document.addEventListener('click', function(event) {
    const loginModal = document.getElementById('login-modal');
    const registerModal = document.getElementById('register-modal');
    
    if (loginModal && event.target === loginModal) {
        hideLogin();
    }
    
    if (registerModal && event.target === registerModal) {
        hideRegister();
    }
});