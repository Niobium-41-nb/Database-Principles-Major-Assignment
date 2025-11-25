function showLogin() { document.getElementById('login-modal').style.display = 'block'; }
function hideLogin() { document.getElementById('login-modal').style.display = 'none'; }
function showRegister() { document.getElementById('register-modal').style.display = 'block'; }
function hideRegister() { document.getElementById('register-modal').style.display = 'none'; }

async function login() {
    const handle = document.getElementById('login-handle').value;
    const password = document.getElementById('login-password').value;
    
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
}

async function register() {
    const handle = document.getElementById('register-handle').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const name = document.getElementById('register-name').value;
    
    const response = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ handle, email, password, name })
    });
    
    const result = await response.json();
    alert(result.message);
    if (result.success) {
        hideRegister();
    }
}

// 检查登录状态
function checkLoginStatus() {
    const userInfo = document.getElementById('user-info');
    const guestButtons = document.getElementById('guest-buttons');
    const userHandle = document.getElementById('user-handle');
    
    // 这里应该从session或localStorage获取用户信息
    // 暂时使用简单的检查方式
    fetch('/api/user/current')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.user) {
                userHandle.textContent = data.user.handle;
                userInfo.style.display = 'block';
                guestButtons.style.display = 'none';
            } else {
                userInfo.style.display = 'none';
                guestButtons.style.display = 'block';
            }
        })
        .catch(() => {
            userInfo.style.display = 'none';
            guestButtons.style.display = 'block';
        });
}

// 登出功能
async function logout() {
    const response = await fetch('/api/logout');
    const result = await response.json();
    alert(result.message);
    if (result.success) {
        location.reload();
    }
}

// 页面加载时检查登录状态
document.addEventListener('DOMContentLoaded', checkLoginStatus);