var qrcode;

window.onload=function(){
    var dropArea = document.getElementById('drop-area')
    
    // 获取二维码对象
    // https://davidshimjs.github.io/qrcodejs/
    qrcode = new QRCode(document.getElementById("qrcode"), {
        width : 143,
        height : 143,
        colorDark : "#ffffff",
        colorLight : "#000000",
        correctLevel : QRCode.CorrectLevel.H
    });

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
}

function uploadFile(file) {
    let url = '/tuchuang/share'
    let formData = new FormData()

    formData.append('file', file)

    fetch(url, {
        method: 'POST',
        body: formData
    })
    .then(function (response) {
        //JavaScript fetch API - 为什么response.json()返回一个promise对象（而不是JSON）
        //https://stackoverflow.com/questions/39435842/javascript-fetch-api-why-does-response-json-return-a-promise-object-instead
        //在 JavaScript 中使用 fetch() 时如何获取响应正文
        //https://byby.dev/js-fetch-get-response-body
        //w3s table
        //https://www.w3schools.com/html/tryit.asp?filename=tryhtml_table_intro
        //https://www.w3schools.com/html/html_tables.asp
        //w3s JS table
        //https://www.w3schools.com/jsref/tryit.asp?filename=tryjsref_table_create
        response.json().then(function(json){
            if(json.state == 'success'){
                //console.log(json); // 打印获取到的数据
                console.log(JSON.stringify(json))
        
                let tr = document.createElement('tr')  
                tr.setAttribute("class", "text-gray-700 dark:text-gray-400");
                let td_name = document.createElement('td')
                td_name.innerText = json.name
                let td_size = document.createElement('td')
                td_size.innerText = json.size
                let td_kind = document.createElement('td')
                td_kind.innerText = json.kind
                let td_date = document.createElement('td')
                td_date.innerText = json.date
                
                // delete and download button
                let td_action = document.createElement('td')
                let action_container = document.createElement('div')
                action_container.setAttribute("class", "button-container");

                let btn_delete = document.createElement('button')
                btn_delete.setAttribute("class","flex items-center justify-between px-0 py-2 text-sm font-medium leading-5 text-purple-600 rounded-lg dark:text-gray-400 focus:outline-none focus:shadow-outline-gray")
                btn_delete.setAttribute("id", "btn_delete");
                btn_delete.setAttribute("onclick", "deleteFile(this)");
                btn_delete.innerText = 'delete'
                action_container.appendChild(btn_delete)

                let btn_download = document.createElement('button')
                btn_download.setAttribute("class","flex items-center justify-between px-1 py-2 text-sm font-medium leading-5 text-purple-600 rounded-lg dark:text-gray-400 focus:outline-none focus:shadow-outline-gray")
                btn_download.setAttribute("id", "btn_download");
                btn_download.setAttribute("onclick", "downloadFile(\""+json.name+"\")");
                btn_download.innerText = 'download'
                action_container.appendChild(btn_download)

                let btn_qr = document.createElement('button')
                btn_qr.setAttribute("class","flex items-center justify-between px-0 py-2 text-sm font-medium leading-5 text-purple-600 rounded-lg dark:text-gray-400 focus:outline-none focus:shadow-outline-gray")
                btn_qr.setAttribute("id", "btn_qr");
                btn_qr.setAttribute("onclick", "makeQRcode(\""+json.name+"\")");
                btn_qr.innerText = 'qrcode'
                action_container.appendChild(btn_qr)
                
                td_action.appendChild(action_container)
                
                //a.setAttribute("href", "/tuchuang/download_share/"+json.name);

                tr.appendChild(td_name)
                tr.appendChild(td_size)
                tr.appendChild(td_kind)
                tr.appendChild(td_date)
                tr.appendChild(td_action)
                //document.getElementById('gallery').appendChild(tr)
                let table_head = document.getElementById('table_head')
                table_head.after(tr);

                //生成新二维码
                makeQRcode(json.name)
            }else if(json.state == 'fail'){
                alert(json.reason);
            }
        });
    })
    .catch(() => { /* Error. Inform the user */ })
}

function handleFiles(files) {
    files = [...files]
    files.forEach(uploadFile)
    
    //input输入框file类型第二次不触发onchange事件
    //https://blog.csdn.net/jianghaha2011/article/details/121821387
    document.getElementById('fileElem').value = ''
}

function deleteFile(btn) {
    var row = btn.parentNode.parentNode.parentNode; // 获取按钮所在的行
    var file_name = row.cells[0].innerText; // 获取第一个单元格的内容

    let url = '/tuchuang/share/delete/'+file_name
    fetch(url) // 指定要获取数据的 URL
    .then(response => response.json()) // 将返回的响应转换为 JSON 格式
        .then(data => {
            console.log(JSON.stringify(data)); // 打印从服务器接收到的数据
        })
    .catch(error => {
        console.error('Error:', error); // 处理错误情况
    });

    row.parentNode.removeChild(row); // 从 DOM 中移除行
    console.log(file_name)
}

function downloadFile(fileName) {
    let url = '/tuchuang/share/download/' + fileName;
    var link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function makeQRcode(fileName) {
    //在黑暗主题下二维码生成的颜色要反过来
    var elements = document.querySelectorAll(".theme-dark");
    if(elements.length == 0){//白天模式
        qrcode._htOption.colorDark = "#000000";
        qrcode._htOption.colorLight = "#ffffff";
    }else{//黑暗模式
        qrcode._htOption.colorDark = "#ffffff";
        qrcode._htOption.colorLight = "#000000";
    }

    //生成新二维码
    var url = document.URL;
    url = url.replace("share", "share/download") + "/" + fileName;
    qrcode.clear();
    qrcode.makeCode(url);
}