let allUsers = [];
let currentUser = null;
let isCurrentUserAdmin = false;

function getRatingClass(rating) {
    if (rating >= 2400) return 'rating-high';
    if (rating >= 1600) return 'rating-medium';
    return 'rating-low';
}

function getAvatarText(handle) {
    return handle.charAt(0).toUpperCase();
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN');
}

// 检查当前用户权限
async function checkCurrentUser() {
    try {
        const response = await fetch('/api/user/current');
        const result = await response.json();

        if (result.success && result.user) {
            currentUser = result.user;
            isCurrentUserAdmin = result.user.is_admin;
        }
    } catch (error) {
        console.error('获取当前用户信息失败:', error);
    }
}

async function loadUsers() {
    try {
        const response = await fetch('/api/users');
        const result = await response.json();

        if (result.success) {
            allUsers = result.users;
            displayUsers(allUsers);
        } else {
            alert('加载用户列表失败: ' + result.message);
        }
    } catch (error) {
        alert('加载用户列表时发生错误: ' + error.message);
    }
}

function displayUsers(users) {
    const usersList = document.getElementById('users-list');
    usersList.innerHTML = '';

    if (users.length === 0) {
        usersList.innerHTML = '<p>暂无用户数据</p>';
        return;
    }

    users.forEach(user => {
        const userItem = document.createElement('div');
        userItem.className = 'user-item';

        const isAdmin = user.is_admin;
        const isCurrentUser = currentUser && user.user_id === currentUser.user_id;

        userItem.innerHTML = `
            <div class="user-avatar">${getAvatarText(user.handle)}</div>
            <div class="user-info">
                <h3 class="user-handle">
                    ${user.handle}
                    ${user.name ? `<span style="color: #666; font-weight: normal;">(${user.name})</span>` : ''}
                    <span class="user-rank">${user.rank}</span>
                    ${isAdmin ? '<span class="admin-badge">管理员</span>' : ''}
                </h3>
                <div class="user-meta">
                    ${user.country ? `
                    <div class="meta-item">
                        <span class="meta-label">国家</span>
                        <span class="meta-value">${user.country}</span>
                    </div>
                    ` : ''}
                    ${user.city ? `
                    <div class="meta-item">
                        <span class="meta-label">城市</span>
                        <span class="meta-value">${user.city}</span>
                    </div>
                    ` : ''}
                    ${user.organization ? `
                    <div class="meta-item">
                        <span class="meta-label">组织</span>
                        <span class="meta-value">${user.organization}</span>
                    </div>
                    ` : ''}
                    <div class="meta-item">
                        <span class="meta-label">最高评分</span>
                        <span class="meta-value">${user.max_rating}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">最高等级</span>
                        <span class="meta-value">${user.max_rank}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">注册时间</span>
                        <span class="meta-value">${formatDate(user.registration_time)}</span>
                    </div>
                </div>
                ${isCurrentUserAdmin && !isCurrentUser ? `
                <div class="user-actions">
                    ${!isAdmin ?
                        `<button class="btn btn-admin" onclick="setAdmin(${user.user_id}, true)">设为管理员</button>` :
                        `<button class="btn btn-remove-admin" onclick="setAdmin(${user.user_id}, false)">取消管理员</button>`
                    }
                </div>
                ` : ''}
            </div>
            <div class="user-rating ${getRatingClass(user.rating)}">
                ${user.rating}
            </div>
        `;

        usersList.appendChild(userItem);
    });
}

function filterUsers() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const rankFilter = document.getElementById('rank-filter').value;
    const ratingFilter = document.getElementById('rating-filter').value;
    const adminFilter = document.getElementById('admin-filter').value;

    let filteredUsers = allUsers.filter(user => {
        // 搜索过滤
        const matchesSearch = user.handle.toLowerCase().includes(searchTerm) ||
                            (user.name && user.name.toLowerCase().includes(searchTerm));

        // 等级过滤
        const matchesRank = !rankFilter || user.rank === rankFilter;

        // 评分过滤
        let matchesRating = true;
        if (ratingFilter) {
            const [min, max] = ratingFilter.split('-').map(val => {
                if (val.endsWith('+')) return parseInt(val) || 0;
                return parseInt(val) || 0;
            });

            if (ratingFilter.endsWith('+')) {
                matchesRating = user.rating >= min;
            } else {
                matchesRating = user.rating >= min && user.rating <= max;
            }
        }

        // 管理员过滤
        let matchesAdmin = true;
        if (adminFilter === 'admin') {
            matchesAdmin = user.is_admin;
        } else if (adminFilter === 'non-admin') {
            matchesAdmin = !user.is_admin;
        }

        return matchesSearch && matchesRank && matchesRating && matchesAdmin;
    });

    displayUsers(filteredUsers);
}

function sortUsers() {
    const sortValue = document.getElementById('sort-filter').value;

    const sortedUsers = [...allUsers].sort((a, b) => {
        switch (sortValue) {
            case 'rating-desc':
                return b.rating - a.rating;
            case 'rating-asc':
                return a.rating - b.rating;
            case 'registration-desc':
                return new Date(b.registration_time) - new Date(a.registration_time);
            case 'registration-asc':
                return new Date(a.registration_time) - new Date(b.registration_time);
            default:
                return 0;
        }
    });

    displayUsers(sortedUsers);
}

// 设置/取消管理员权限
async function setAdmin(userId, isAdmin) {
    if (!confirm(`确定要${isAdmin ? '设为' : '取消'}管理员权限吗？`)) {
        return;
    }

    try {
        const response = await fetch('/api/user/set_admin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                is_admin: isAdmin
            })
        });

        const result = await response.json();
        if (result.success) {
            alert(result.message);
            // 重新加载用户列表
            await loadUsers();
        } else {
            alert('操作失败: ' + result.message);
        }
    } catch (error) {
        alert('操作失败: ' + error.message);
    }
}

// 页面加载时获取用户列表和当前用户信息
document.addEventListener('DOMContentLoaded', async function() {
    await checkCurrentUser();
    await loadUsers();
});