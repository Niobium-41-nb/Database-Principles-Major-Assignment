function showHackDialog() {
    document.getElementById('hackDialog').style.display = 'block';
}

function closeHackDialog() {
    document.getElementById('hackDialog').style.display = 'none';
}

// 从DOM中获取submission_id
function getSubmissionId() {
    const urlParts = window.location.pathname.split('/');
    for (let i = 0; i < urlParts.length; i++) {
        if (urlParts[i] === 'submission' && i + 1 < urlParts.length) {
            const submissionId = urlParts[i + 1];
            if (submissionId && submissionId.match(/^\d+$/)) {
                return submissionId;
            }
        }
    }
    return null;
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    const hackForm = document.getElementById('hackForm');
    if (hackForm) {
        hackForm.onsubmit = function(e) {
            e.preventDefault();
            const hackInput = document.getElementById('hackInput').value;
            const hackOutput = document.getElementById('hackOutput').value;
            const submissionId = getSubmissionId();

            if (!submissionId) {
                alert('无法获取提交ID');
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
                    alert('Hack提交失败：' + data.message);
                }
            })
            .catch(error => {
                alert('操作失败：' + error);
            })
            .finally(() => {
                closeHackDialog();
            });
        };
    }
});