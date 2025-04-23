function deleteFile(fileId) {
    if (confirm('确定要删除这个文件吗？')) {
        // 使用Django的CSRF token
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch(`/admin/ai_app/uploadedfile/${fileId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
        })
        .then(response => {
            if (response.ok) {
                // 刷新页面
                window.location.reload();
            } else {
                alert('删除失败');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('删除失败');
        });
    }
}

// 重命名文件的弹窗
function renameFile(fileId) {
    const newName = prompt('请输入新的文件名：');
    if (newName) {
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const formData = new FormData();
        formData.append('new_name', newName);
        
        fetch(`/admin/ai_app/uploadedfile/${fileId}/rename/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            body: formData
        })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                alert('重命名失败');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('重命名失败');
        });
    }
} 