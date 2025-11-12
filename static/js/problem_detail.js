// 页面加载时获取题目数据
document.addEventListener('DOMContentLoaded', function() {
    const problemId = window.location.pathname.split('/').pop();
    loadProblemDetail(problemId);

    // 提交表单处理
    const submitForm = document.getElementById('submit-form');
    if (submitForm) {
        submitForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitSolution(problemId);
        });
    }
});

function loadProblemDetail(problemId) {
    fetch(`/api/problem/${problemId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayProblem(data.problem);
            } else {
                showError(data.message || '获取题目详情失败');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('网络错误，请稍后重试');
        });
}

function displayProblem(problem) {
    // 隐藏加载中，显示内容
    document.getElementById('loading').style.display = 'none';
    document.getElementById('problem-content').style.display = 'block';

    // 更新页面标题
    document.title = problem.title + ' - 在线评测系统';

    // 更新题目信息
    document.getElementById('problem-title').textContent = problem.title;
    document.getElementById('statement').innerHTML = problem.statement || '<p>暂无题目描述</p>';
    document.getElementById('input-spec').innerHTML = problem.input_specification || '<p>暂无输入格式说明</p>';
    document.getElementById('output-spec').innerHTML = problem.output_specification || '<p>暂无输出格式说明</p>';
    document.getElementById('time-limit').textContent = problem.time_limit;
    document.getElementById('memory-limit').textContent = problem.memory_limit;
    document.getElementById('accepted-count').textContent = problem.accepted_count || 0;
    document.getElementById('submission-count').textContent = problem.submission_count || 0;

    // 设置难度
    const difficultyBadge = document.getElementById('difficulty-badge');
    const colors = {
        '简单': 'bg-success',
        '中等': 'bg-warning',
        '困难': 'bg-danger',
        'Easy': 'bg-success',
        'Medium': 'bg-warning',
        'Hard': 'bg-danger'
    };
    difficultyBadge.textContent = problem.difficulty || '简单';
    difficultyBadge.className = `badge ${colors[problem.difficulty] || 'bg-secondary'}`;

    // 更新标签
    const tagsContainer = document.getElementById('tags-container');
    if (problem.tags && problem.tags.length > 0) {
        tagsContainer.innerHTML = '';
        problem.tags.forEach(tag => {
            const tagElement = document.createElement('span');
            tagElement.className = 'tag';
            tagElement.textContent = tag;
            tagsContainer.appendChild(tagElement);
        });
    } else {
        tagsContainer.innerHTML = '<span class="text-muted">暂无标签</span>';
    }

    // 更新样例
    const samplesContainer = document.getElementById('samples-container');
    const samplesCard = document.getElementById('samples-card');
    if (problem.sample_tests && problem.sample_tests.length > 0) {
        samplesCard.style.display = 'block';
        samplesContainer.innerHTML = '';

        problem.sample_tests.forEach((sample, index) => {
            const sampleElement = document.createElement('div');
            sampleElement.className = 'sample-test';
            sampleElement.innerHTML = `
                <strong>样例 ${index + 1}:</strong>
                <div class="mt-2">
                    <strong>输入:</strong>
                    <div class="code-block">${sample.input || ''}</div>
                </div>
                <div class="mt-2">
                    <strong>输出:</strong>
                    <div class="code-block">${sample.output || ''}</div>
                </div>
            `;
            samplesContainer.appendChild(sampleElement);
        });

        // 渲染代码高亮
        if (typeof hljs !== 'undefined') {
            document.querySelectorAll('.code-block').forEach(block => {
                hljs.highlightElement(block);
            });
        }
    } else {
        samplesCard.style.display = 'none';
    }
}

function showError(message) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('error-message').style.display = 'block';
    document.getElementById('error-text').textContent = message;
}

function submitSolution(problemId) {
    const sourceCode = document.getElementById('source-code').value;
    const language = document.getElementById('language').value;

    if (!sourceCode.trim()) {
        alert('请填写代码');
        return;
    }

    fetch('/api/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            problem_id: problemId,
            source_code: sourceCode,
            language: language
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('提交成功！提交ID: ' + data.submission_id);
            window.location.href = '/submissions';
        } else {
            alert('提交失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('提交失败');
    });
}