window.onload=function(){
    var dropArea = document.getElementById('drop-area')

    var filesDone = 0
    var filesToDo = 0
    var progressBar = document.getElementById('progress-bar')

    // 阻止默认行为
    ;['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false)
    })

    function preventDefaults (e) {
        e.preventDefault()
        e.stopPropagation()
    }

    // 增加事件，鼠标拖入边框高亮，拖出边框变为原来样子
    ;['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false)
    })

    ;['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false)
    })

    function highlight(e) {
        dropArea.classList.add('highlight')
    }

    function unhighlight(e) {
        dropArea.classList.remove('highlight')
    }

    // 增加事件，鼠标放下，之后准备上传图片
    dropArea.addEventListener('drop', handleDrop, false)

    function handleDrop(e) {
        let dt = e.dataTransfer
        let files = dt.files

        handleFiles(files)
    }

    function uploadFile(file) {
        let url = 'http://127.0.0.1:5000/tuchuang/'
        let formData = new FormData()

        formData.append('file', file)

        fetch(url, {
            method: 'POST',
            body: formData
        })
            .then(progressDone) // <- Add `progressDone` call here
            .catch(() => { /* Error. Inform the user */ })
    }

    // 预览
    function previewFile(file) {
        let reader = new FileReader()
        reader.readAsDataURL(file)
        reader.onloadend = function() {
            let img = document.createElement('img')
            img.src = reader.result
            document.getElementById('gallery').appendChild(img)
        }
    }

    function handleFiles(files) {
        files = [...files]
        initializeProgress(files.length) // <- Add this line
        files.forEach(uploadFile)
        files.forEach(previewFile)
    }

    // 进度条
    function initializeProgress(numfiles) {
        progressBar.value = 0
        filesDone = 0
        filesToDo = numfiles
    }

    function progressDone() {
        filesDone++
        progressBar.value = filesDone / filesToDo * 100
    }
}
