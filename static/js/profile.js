// static/js/profile.js - 个人资料页面专用功能

let currentUser = null;

function getRatingClass(rating) {
    if (rating >= 2400) return 'rating-high';
    if (rating >= 1600) return 'rating-medium';
    return 'rating-low';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', {hour: '2-digit', minute: '2-digit'});
}

function showMessage(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="message ${type}">${message}</div>`;
    setTimeout(() => {
        element.innerHTML = '';
    }, 5000);
}

function switchTab(tabName) {
    // 隐藏所有标签内容
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    // 移除所有标签的激活状态
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    // 显示选中的标签内容
    document.getElementById(tabName).classList.add('active');
    // 激活选中的标签
    event.target.classList.add('active');
}

function updateAvatar(avatarElement, avatarUrl, handle) {
    if (avatarUrl && avatarUrl.trim() !== '') {
        // 设置背景图片
        avatarElement.style.backgroundImage = `url('${avatarUrl}')`;
        avatarElement.textContent = ''; // 清除文字
        avatarElement.style.backgroundColor = 'transparent'; // 移除背景色
    } else {
        // 没有头像URL时显示首字母
        avatarElement.style.backgroundImage = 'none';
        avatarElement.textContent = handle.charAt(0).toUpperCase();
        avatarElement.style.backgroundColor = '#3498db'; // 恢复背景色
    }
}

async function loadUserProfile() {
    try {
        const response = await fetch('/api/user/current');
        const result = await response.json();

        if (result.success) {
            currentUser = result.user;
            displayUserProfile(currentUser);
            document.getElementById('profile-content').style.display = 'block';
        } else {
            document.getElementById('login-prompt').style.display = 'block';
        }
    } catch (error) {
        console.error('加载用户资料失败:', error);
        document.getElementById('login-prompt').style.display = 'block';
    }
}

function displayUserProfile(user) {
    const avatarElement = document.getElementById('user-avatar');

    // 更新头像
    updateAvatar(avatarElement, user.avatar, user.handle);

    // 更新用户名和评分
    document.getElementById('user-handle').textContent = user.handle;
    const ratingElement = document.getElementById('user-rating');
    ratingElement.textContent = user.rating;
    ratingElement.className = getRatingClass(user.rating);

    // 更新用户信息
    const userMeta = document.getElementById('user-meta');
    userMeta.innerHTML = `
        <div class="meta-item">
            <span class="meta-label">姓名</span>
            <span class="meta-value">${user.name || '未设置'}</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">邮箱</span>
            <span class="meta-value">${user.email}</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">等级</span>
            <span class="meta-value">${user.rank}</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">最高评分</span>
            <span class="meta-value">${user.max_rating}</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">国家</span>
            <span class="meta-value">${user.country || '未设置'}</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">城市</span>
            <span class="meta-value">${user.city || '未设置'}</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">组织</span>
            <span class="meta-value">${user.organization || '未设置'}</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">注册时间</span>
            <span class="meta-value">${formatDate(user.registration_time)}</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">最后在线</span>
            <span class="meta-value">${formatDate(user.last_online_time)}</span>
        </div>
    `;

    // 填充表单
    document.getElementById('name').value = user.name || '';
    document.getElementById('country').value = user.country || '';
    document.getElementById('city').value = user.city || '';
    document.getElementById('organization').value = user.organization || '';
    document.getElementById('avatar').value = user.avatar || '';
}

// 处理个人资料表单提交
document.getElementById('profile-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = {
        name: document.getElementById('name').value,
        country: document.getElementById('country').value,
        city: document.getElementById('city').value,
        organization: document.getElementById('organization').value,
        avatar: document.getElementById('avatar').value
    };

    try {
        const response = await fetch('/api/user/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (result.success) {
            showMessage('profile-message', '个人资料更新成功', 'success');
            // 更新当前用户数据
            if (currentUser) {
                currentUser = {...currentUser, ...formData};
                updateAvatar(document.getElementById('user-avatar'), formData.avatar, currentUser.handle);
            }
            // 重新加载用户资料
            loadUserProfile();
        } else {
            showMessage('profile-message', result.message, 'error');
        }
    } catch (error) {
        showMessage('profile-message', '更新失败: ' + error.message, 'error');
    }
});

// 处理密码修改表单提交
document.getElementById('password-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const oldPassword = document.getElementById('old-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (newPassword !== confirmPassword) {
        showMessage('password-message', '新密码和确认密码不一致', 'error');
        return;
    }

    if (newPassword.length < 6) {
        showMessage('password-message', '新密码长度至少为6位', 'error');
        return;
    }

    try {
        const response = await fetch('/api/user/change_password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                old_password: oldPassword,
                new_password: newPassword
            })
        });

        const result = await response.json();

        if (result.success) {
            showMessage('password-message', '密码修改成功', 'success');
            document.getElementById('password-form').reset();
        } else {
            showMessage('password-message', result.message, 'error');
        }
    } catch (error) {
        showMessage('password-message', '密码修改失败: ' + error.message, 'error');
    }
});

// 页面加载时获取用户资料
document.addEventListener('DOMContentLoaded', loadUserProfile);