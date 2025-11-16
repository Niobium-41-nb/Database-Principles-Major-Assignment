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

    fetch('/api/hack/{{ detail.submission_id }}', {
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