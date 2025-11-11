let tags = [];
let testCaseCount = 1;

// 检查登录状态
function checkLoginStatus() {
    const userInfo = document.getElementById('user-info');
    const guestButtons = document.getElementById('guest-buttons');
    const userHandle = document.getElementById('user-handle');

    fetch('/api/user/current')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.user) {
                userHandle.textContent = data.user.handle;
                userInfo.style.display = 'block';
                guestButtons.style.display = 'none';

                // 检查是否是管理员
                if (!data.user.is_admin) {
                    alert('只有管理员可以创建题目');
                    window.location.href = '/problems';
                }
            } else {
                userInfo.style.display = 'none';
                guestButtons.style.display = 'block';
                alert('请先登录');
                window.location.href = '/problems';
            }
        })
        .catch(() => {
            userInfo.style.display = 'none';
            guestButtons.style.display = 'block';
            alert('请先登录');
            window.location.href = '/problems';
        });
}

// 标签管理
function addTag() {
    const tagInput = document.getElementById('tag-input');
    const tag = tagInput.value.trim();

    if (tag && !tags.includes(tag)) {
        tags.push(tag);
        updateTagsDisplay();
        tagInput.value = '';
    }
}

function removeTag(tag) {
    tags = tags.filter(t => t !== tag);
    updateTagsDisplay();
}

function updateTagsDisplay() {
    const container = document.getElementById('tags-container');
    const hiddenInput = document.getElementById('tags');

    container.innerHTML = '';
    tags.forEach(tag => {
        const tagElement = document.createElement('div');
        tagElement.className = 'tag';
        tagElement.innerHTML = `
            ${tag}
            <span class="remove-tag" onclick="removeTag('${tag}')">×</span>
        `;
        container.appendChild(tagElement);
    });

    hiddenInput.value = JSON.stringify(tags);
}

// 测试用例管理
function addTestCase() {
    testCaseCount++;
    const testCasesContainer = document.getElementById('test-cases');
    const newTestCase = document.createElement('div');
    newTestCase.className = 'test-case';
    newTestCase.innerHTML = `
        <div class="test-case-header">
            <span>测试用例 #${testCaseCount}</span>
            <button type="button" class="btn btn-secondary" onclick="removeTestCase(this)">删除</button>
        </div>
        <label>输入</label>
        <textarea name="test_input" placeholder="输入数据"></textarea>
        <label>期望输出</label>
        <textarea name="test_output" placeholder="期望输出"></textarea>
        <label>
            <input type="checkbox" name="is_sample"> 作为样例显示
        </label>
    `;
    testCasesContainer.appendChild(newTestCase);
}

function removeTestCase(button) {
    if (testCaseCount > 1) {
        const testCase = button.closest('.test-case');
        testCase.remove();
        testCaseCount--;
        // 重新编号
        const testCases = document.querySelectorAll('.test-case');
        testCases.forEach((testCase, index) => {
            testCase.querySelector('.test-case-header span').textContent = `测试用例 #${index + 1}`;
        });
    } else {
        alert('至少需要一个测试用例');
    }
}

// 表单提交
document.getElementById('create-problem-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const data = {
        problem_id: formData.get('problem_id'),
        title: formData.get('title'),
        statement: formData.get('statement'),
        input_specification: formData.get('input_specification'),
        output_specification: formData.get('output_specification'),
        time_limit: parseInt(formData.get('time_limit')),
        memory_limit: parseInt(formData.get('memory_limit')),
        difficulty: formData.get('difficulty'),
        notes: formData.get('notes'),
        tags: JSON.parse(formData.get('tags') || '[]')
    };

    // 收集测试用例
    data.test_cases = [];
    const testCases = document.querySelectorAll('.test-case');
    testCases.forEach((testCase, index) => {
        const inputs = testCase.querySelectorAll('textarea');
        const checkbox = testCase.querySelector('input[type="checkbox"]');
        data.test_cases.push({
            input: inputs[0].value,
            output: inputs[1].value,
            is_sample: checkbox.checked,
            test_order: index + 1
        });
    });

    // 验证必填字段
    const errors = validateForm(data);
    if (Object.keys(errors).length > 0) {
        displayErrors(errors);
        return;
    }

    try {
        const response = await fetch('/api/problems/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (result.success) {
            alert('题目创建成功！');
            window.location.href = `/problem/${data.problem_id}`;
        } else {
            alert('创建失败: ' + result.message);
        }
    } catch (error) {
        alert('创建失败: ' + error.message);
    }
});

function validateForm(data) {
    const errors = {};

    if (!data.problem_id.trim()) {
        errors.problem_id = '题目ID不能为空';
    }

    if (!data.title.trim()) {
        errors.title = '题目标题不能为空';
    }

    if (!data.statement.trim()) {
        errors.statement = '题目描述不能为空';
    }

    if (data.time_limit < 100) {
        errors.time_limit = '时间限制不能小于100ms';
    }

    if (data.memory_limit < 1000) {
        errors.memory_limit = '内存限制不能小于1000KB';
    }

    if (data.test_cases.length === 0) {
        alert('至少需要一个测试用例');
    }

    return errors;
}

function displayErrors(errors) {
    // 清除所有错误显示
    document.querySelectorAll('.error').forEach(el => el.textContent = '');

    // 显示新的错误
    Object.keys(errors).forEach(field => {
        const errorElement = document.getElementById(`${field}-error`);
        if (errorElement) {
            errorElement.textContent = errors[field];
        }
    });
}

// 登录相关函数（与problems.html相同）
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

async function register() {
    const handle = document.getElementById('register-handle').value;
    const email = document.getElementById('register-email').value;
    const name = document.getElementById('register-name').value;
    const password = document.getElementById('register-password').value;

    if (!handle || !email || !password) {
        alert('请填写必填信息');
        return;
    }

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ handle, email, name, password })
        });

        const result = await response.json();
        alert(result.message);
        if (result.success) {
            hideRegister();
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

// 页面加载时执行
document.addEventListener('DOMContentLoaded', function() {
    checkLoginStatus();
});