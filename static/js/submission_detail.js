function showHackDialog() {
    document.getElementById('hackDialog').style.display = 'block';
}

function closeHackDialog() {
    document.getElementById('hackDialog').style.display = 'none';
}

document.getElementById('hackForm').onsubmit = function(e) {
    e.preventDefault();
    const hackInput = document.getElementById('hackInput').value;
    const hackOutput = document.getElementById('hackOutput').value;

    // 从表单的 data 属性中读取 submission id，避免在静态文件中使用模板变量
    const submissionId = this.dataset.submissionId;
    if (!submissionId) {
        alert('无法识别提交 ID，操作取消');
        closeHackDialog();
        return;
    }

    fetch(`/api/hack/${submissionId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            input: hackInput,
            output: hackOutput
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Hack成功提交！');
            location.reload();
        } else {
            alert('Hack提交失败：' + (data.message || '未知错误'));
        }
    })
    .catch(error => {
        alert('操作失败：' + error);
    })
    .finally(() => {
        closeHackDialog();
    });
};