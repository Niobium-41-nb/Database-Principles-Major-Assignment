// static/js/profile.js - 个人资料页面专用功能

let currentUser = null;
let isSubmitting = false;

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

function validateForm(formData) {
    // 检查URL格式（如果提供了头像URL）
    if (formData.avatar && formData.avatar.trim() !== '') {
        try {
            new URL(formData.avatar);
        } catch (e) {
            return '头像URL格式不正确，请输入有效的URL地址';
        }
    }
    
    return null;
}

function setLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.innerHTML = '<span class="loading"></span> 处理中...';
    } else {
        button.disabled = false;
        button.textContent = button.getAttribute('data-original-text');
    }
}

async function loadUserProfile() {
    console.log('开始加载用户资料...');
    try {
        const response = await fetch('/api/user/current');
        console.log('API响应状态:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP错误: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('API响应数据:', result);

        if (result.success) {
            currentUser = result.user;
            console.log('当前用户:', currentUser);
            displayUserProfile(currentUser);
            document.getElementById('profile-content').style.display = 'block';
            document.getElementById('login-prompt').style.display = 'none';
        } else {
            console.log('用户未登录或认证失败:', result.message);
            document.getElementById('login-prompt').style.display = 'block';
            document.getElementById('profile-content').style.display = 'none';
        }
    } catch (error) {
        console.error('加载用户资料失败:', error);
        document.getElementById('login-prompt').style.display = 'block';
        document.getElementById('profile-content').style.display = 'none';
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
    
    if (isSubmitting) return;
    isSubmitting = true;

    const submitButton = this.querySelector('button[type="submit"]');
    submitButton.setAttribute('data-original-text', submitButton.textContent);
    setLoading(submitButton, true);

    const formData = {
        name: document.getElementById('name').value.trim(),
        country: document.getElementById('country').value.trim(),
        city: document.getElementById('city').value.trim(),
        organization: document.getElementById('organization').value.trim(),
        avatar: document.getElementById('avatar').value.trim()
    };

    // 验证表单
    const validationError = validateForm(formData);
    if (validationError) {
        showMessage('profile-message', validationError, 'error');
        setLoading(submitButton, false);
        isSubmitting = false;
        return;
    }

    try {
        const response = await fetch('/api/user/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();
        console.log('更新个人资料响应:', result);

        if (result.success) {
            showMessage('profile-message', '个人资料更新成功！', 'success');
            // 更新当前用户数据
            if (currentUser) {
                currentUser = {...currentUser, ...formData};
                updateAvatar(document.getElementById('user-avatar'), formData.avatar, currentUser.handle);
            }
            // 重新加载用户资料以更新显示
            setTimeout(() => {
                loadUserProfile();
            }, 1000);
        } else {
            showMessage('profile-message', result.message || '更新失败，请稍后重试', 'error');
        }
    } catch (error) {
        console.error('更新个人资料错误:', error);
        showMessage('profile-message', '更新失败: ' + error.message, 'error');
    } finally {
        setLoading(submitButton, false);
        isSubmitting = false;
    }
});

// 处理密码修改表单提交
document.getElementById('password-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (isSubmitting) return;
    isSubmitting = true;

    const submitButton = this.querySelector('button[type="submit"]');
    submitButton.setAttribute('data-original-text', submitButton.textContent);
    setLoading(submitButton, true);

    const oldPassword = document.getElementById('old-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (newPassword !== confirmPassword) {
        showMessage('password-message', '新密码和确认密码不一致', 'error');
        setLoading(submitButton, false);
        isSubmitting = false;
        return;
    }

    if (newPassword.length < 6) {
        showMessage('password-message', '新密码长度至少为6位', 'error');
        setLoading(submitButton, false);
        isSubmitting = false;
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
        console.log('修改密码响应:', result);

        if (result.success) {
            showMessage('password-message', '密码修改成功！', 'success');
            document.getElementById('password-form').reset();
        } else {
            showMessage('password-message', result.message || '密码修改失败', 'error');
        }
    } catch (error) {
        console.error('修改密码错误:', error);
        showMessage('password-message', '密码修改失败: ' + error.message, 'error');
    } finally {
        setLoading(submitButton, false);
        isSubmitting = false;
    }
});

// 页面加载时获取用户资料
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成，开始初始化...');
    loadUserProfile();
    
    // 添加表单输入监听，实时验证
    document.getElementById('avatar').addEventListener('blur', function() {
        const url = this.value.trim();
        if (url && url !== '') {
            try {
                new URL(url);
                this.style.borderColor = '#27ae60';
            } catch (e) {
                this.style.borderColor = '#e74c3c';
            }
        } else {
            this.style.borderColor = '#ddd';
        }
    });
});