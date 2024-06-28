document.getElementById('imageUpload').addEventListener('change', function(event) {
    const file = event.target.files[0];
    const imagePreview = document.getElementById('imagePreview');

    if (file) {
        const img = new Image();
        img.onload = function() {
            if (this.width === 240 && this.height === 240) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.style.display = 'flex';
                    imagePreview.innerHTML = '<img src="' + e.target.result + '" alt="Image Preview">';
                }
                reader.readAsDataURL(file);
            } else {
                alert('Image must be exactly 240x240 pixels');
                imagePreview.style.display = 'none';
                imagePreview.innerHTML = '';
                document.getElementById('imageUpload').value = ''; // Reset file input
            }
        }
        img.src = URL.createObjectURL(file);
    } else {
        imagePreview.style.display = 'none';
        imagePreview.innerHTML = '';
    }
});

document.addEventListener('DOMContentLoaded', function() {
    fetch('/pcb/create/get_categories')  // 替换为实际的端点URL
        .then(response => response.json())
        .then(existingCategories => {
            const existingCategoriesSpan = document.getElementById('existingCategories');
            existingCategoriesSpan.innerHTML = ''; // 清空现有内容

            existingCategories.forEach((category, index) => {
                // 创建并添加类别到现有类别列表
                const label = document.createElement('label');
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = category;
                label.appendChild(checkbox);
                label.appendChild(document.createTextNode(category));
                const categoryItem = document.createElement('span');
                categoryItem.classList.add('category-item');
                categoryItem.appendChild(label);

                existingCategoriesSpan.appendChild(categoryItem);
            });
        })
        .catch(error => {
            console.error('获取类别时出错:', error);
            // 可以在此处处理错误，例如向用户显示错误消息
        });
});

function addCategory() {
    const newCategoryInput = document.getElementById('newCategory');
    const newCategory = newCategoryInput.value.trim();
    const existingCategoriesSpan = document.getElementById('existingCategories');

    if (newCategory !== "") {
        let exists = false;
        for (let checkbox of existingCategoriesSpan.querySelectorAll('input[type="checkbox"]')) {
            if (checkbox.value === newCategory) {
                exists = true;
                break;
            }
        }

        if (!exists) {
            // 发送新类别到云端
            fetch('/pcb/create/add_category', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ category: newCategory }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to add category');
                }
                return response.json();
            })
            .then(data => {
                // 添加到现有类别列表
                const label = document.createElement('label');
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = newCategory;
                label.appendChild(checkbox);
                label.appendChild(document.createTextNode(newCategory));
                const categoryItem = document.createElement('span');
                categoryItem.classList.add('category-item');
                categoryItem.appendChild(label);
                existingCategoriesSpan.appendChild(categoryItem);
                newCategoryInput.value = ''; // 清空输入框
            })
            .catch(error => {
                console.error('添加类别时出错:', error);
                // 可以在此处处理错误，例如向用户显示错误消息
            });
        } else {
            alert('类别已存在');
        }
    } else {
        alert('请输入类别');
    }
}

function handleFormSubmit(event) {
    // Prevent the form from submitting immediately
    event.preventDefault();

    // Get all selected categories
    const selectedCategories = [];
    const checkboxes = document.querySelectorAll('#existingCategories input[type="checkbox"]:checked');
    checkboxes.forEach(checkbox => {
        selectedCategories.push(checkbox.value);
    });

    // Set the value of the hidden input field
    document.getElementById('selectedCategories').value = selectedCategories.join(',');

    // Submit the form
    document.getElementById('myForm').submit();
}

