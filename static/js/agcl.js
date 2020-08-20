async function on_sub(a_el_id, td_sel_id, sub_id){
    remove_tbl_rows()
    // alert('Function: on_sub\nsub_id: ' + sub_id + '\na_el_id: ' + a_el_id)
    var td_el = document.getElementById(td_sel_id);
    while(td_el.lastElementChild.id != a_el_id){
        td_el.removeChild(td_el.lastElementChild);
    }

    // var sel_el = document.getElementById(sub_id);
    // alert(sel_el.innerText);
    var a_el = document.getElementById(a_el_id)
    // alert(a_el.id)
    // alert('home_id.id: ' + home_id + '\ntd_sel_id.id: ' + td_sel_id + '\nsub_id text: ' + sub_id)
    let tag_el = await make_el(sel_text=a_el.id, sel_id=sub_id);
    // alert('tag_el.tagname: ' + tag_el.tagName)
    if(tag_el != null){
        if(tag_el.tagName == "SELECT"){
            tag_el.setAttribute("onchange", 'on_select(td_sel_id="'+td_el.id+'", sub_id="'+tag_el.id+'")');
            td_el.appendChild(tag_el);
        }
        else if(tag_el.tagName == "A"){ 
            while(tag_el.tagName == 'A'){
                var span_el = document.createElement('span')
                span_el.innerText = ' / '
                td_el.appendChild(span_el)
                tag_el.setAttribute("onclick", 'on_sub(a_el_id="'+tag_el.id+'", td_sel_id="'+td_el.id+'", sub_id="'+tag_el.id+'")');
                td_el.appendChild(tag_el);
                tag_el = await make_el(sel_text=tag_el.id, sel_id=sub_id)
            }
            if(tag_el.tagName == 'SELECT'){
                var span_el = document.createElement('span')
                span_el.innerText = ' '
                td_el.appendChild(span_el)
                tag_el.setAttribute("onchange", 'on_select(td_sel_id="'+td_el.id+'", sub_id="'+tag_el.id+'")');
                td_el.appendChild(tag_el);
            }
            else if(tag_el.tagName == null){
                alert("Null tagName!")
            }
        }
    }
}


function remove_tbl_rows(){
    tbl = document.getElementById('tbl_1')
    while(tbl.lastElementChild.tagName == 'TR'){
        tbl.removeChild(tbl.lastElementChild);
    };
}


async function on_home(td_sel_id){
    remove_tbl_rows()
    const td_el = document.getElementById(td_sel_id);
    const home_el = td_el.firstElementChild
    // alert('home_el id: ' + home_el.id)
    var sel_id = 'sel_' + home_el.id.split('_').slice(-1).pop()
    // alert('sel_id: ' + sel_id)
    while(td_el.lastElementChild != home_el){
        if(td_el.lastElementChild.tagName == 'SELECT'){
            sel_id = td_el.lastElementChild.id
        }
        td_el.removeChild(td_el.lastElementChild);
    }
    let tag_el = await make_el(sel_text='/init', sel_id=sel_id);
    // alert('tag_el.tagname: ' + tag_el.tagName)
    if(tag_el != null){
        if(tag_el.tagName == "SELECT"){
            tag_el.setAttribute("onchange", 'on_select(td_sel_id="'+td_sel_id+'", sub_id="'+tag_el.id+'")');
            td_el.appendChild(tag_el);
        }
        else if(select1_tag.tagName == "A"){ 
            tag_el.setAttribute("onclick", 'on_sub(a_el_id="'+tag_el.id+'", td_sel_id="'+td_el.id+'", sub_id="'+repl_a.id+'")');
            td_el.appendChild(tag_el);
        }
    }
}


async function on_select(td_sel_id, sub_id){
    // alert('function: on_select')
    remove_tbl_rows()
    var td_el = document.getElementById(td_sel_id)
    var sel_el = document.getElementById(sub_id)
    var sel_text = sel_el.options[sel_el.selectedIndex].text;
    var sel_value = sel_el.options[sel_el.selectedIndex].value;
    var span_el = document.createElement('span')
    span_el.innerText = ' / '
    var repl_a = document.createElement('a');
    repl_a.innerHTML = '<span>' + sel_text + '</span>';
    // repl_a.innertHTML = sel_text
    repl_a.href = '#'
    repl_a.id = '/' + sel_value;

    const select_tag_id = sel_el.id
    repl_a.setAttribute("onclick", 'on_sub(a_el_id="'+repl_a.id+'", td_sel_id="'+td_el.id+'", sub_id="'+repl_a.id+'")');
    td_el.replaceChild(span_el, sel_el)
    td_el.appendChild(repl_a)
    // td_el.replaceChild(repl_a, sel_el)

    let tag_el = await make_el(sel_text=repl_a.id, sel_id=select_tag_id);
    // alert('tag_el.tagname: ' + tag_el.tagName)
    if(tag_el != null){
        if(tag_el.tagName == "SELECT"){
            tag_el.setAttribute("onchange", 'on_select(td_sel_id="'+td_sel_id+'", sub_id="'+tag_el.id+'")');
            td_el.appendChild(tag_el);
        }
        else if(tag_el.tagName == "A"){
            while(tag_el.tagName == 'A'){
                var span_el = document.createElement('span')
                span_el.innerText = ' / '
                td_el.appendChild(span_el)
                tag_el.setAttribute("onclick", 'on_sub(a_el_id="'+tag_el.id+'", td_sel_id="'+td_el.id+'", sub_id="'+tag_el.id+'")');
                td_el.appendChild(tag_el);
                tag_el = await make_el(sel_text=tag_el.id, sel_id=sub_id)
            }
            if(tag_el.tagName == 'SELECT'){
                var span_el = document.createElement('span')
                span_el.innerText = ' '
                td_el.appendChild(span_el)
                tag_el.setAttribute("onchange", 'on_select(td_sel_id="'+td_el.id+'", sub_id="'+tag_el.id+'")');
                td_el.appendChild(tag_el);
            }
        }
    }
    else if(tag_el == null){
        let fl = await ajax_get_file_list(sel_value)
        show_images(fl)
    }
}


function show_images(fl){
    tbl = document.getElementById('tbl_1')
    for(f in fl.sort().reverse()){
        fn = fl[f].split('/').slice(-1).pop();
        tr_el = document.createElement('tr')
        td_name_el = document.createElement('td')
        td_name_el.innerHTML = '<span> </span>' + fn + '<span>&nbsp&nbsp</span>'
        td_img_el = document.createElement('td')
        td_img_el.innerHTML = '<img src=' + fl[f] + '></img>'
        tr_el.appendChild(td_name_el)
        tr_el.appendChild(td_img_el)
        tbl.appendChild(tr_el)
    }
}



function ajax_get_file_list(file_path){
    // alert('function: ajax_get_dirs')
    return new Promise((resolve, reject) => {
        $.ajax({
            url: 'fileList/' + file_path,
            type: "get",
            success: function(response) {
                resolve(response);
            },
            error:  function(xhr) {
                resolve(null)
            }
        });  // close ajax
    }); //close promise
}  // close function



function ajax_get_dirs(sel_text){
    // alert('function: ajax_get_dirs')
    return new Promise((resolve, reject) => {
        $.ajax({
            url: sel_text,
            type: "get",
            success: function(response) {
                resolve(response);
            },
            error:  function(xhr) {
                resolve(null)
            }
        });  // close ajax
    }); //close promise
}  // close function


async function make_el(sel_text, sel_id){
    // alert('function: make_el')
    let response = await ajax_get_dirs(sel_text=sel_text)
    // alert(response)
    return new Promise((resolve, reject) => {
        // alert('response: ' + response + '\nresponse length: ' + response.length)
        if(response.length > 2){
            var select_tag = document.createElement('select');
            var sel_tag_id = sel_id + '1'
            select_tag.id = sel_tag_id
            //foreach key create option element and append to select element
            var x = 0
            for(key in response){
                var opt = document.createElement('option');
                opt.value = response[key];
                opt.innerText = response[key].split('/').slice(-1).pop();
                if(x==0){
                    opt.selected = true
                }
                select_tag.appendChild(opt);
                x = x + 1
            }
            resolve(select_tag)
        }
        else if(response.length > 1){
            var a_el = document.createElement('a')
            // a_el.innerText = 'id: ' + sel_text + ' ';
            last_key = response.slice(-1).pop().split('/').slice(-1).pop();
            a_el.innerHTML = '<span>' + last_key + '</span>';
            a_el.href = '#'
            a_el.id = '/' + response.slice(-1).pop();  // sel_id
            resolve(a_el)
    
        }
        else {
            resolve(null)
        }
    });
}

async function on_sel_id(home_id, td_sel_id, sel_id) {
    var td_el = document.getElementById(td_sel_id)
    var sel_el = document.getElementById(sel_id)
    var home_el = document.getElementById(home_id);
    var sel_value = sel_el.options[sel_el.selectedIndex].value;
    var sel_text = sel_el.options[sel_el.selectedIndex].text;
    if(sel_value!=0){
        var repl_a = document.createElement('a');
        repl_a.innerText = 'id: ' + sel_text + ' ';
        repl_a.href = '#'
        repl_a.id = '/' + sel_text;  // sel_id
        repl_a.setAttribute("onclick", 'on_sub(a_el_id="'+repl_a.id+'", td_sel_id="'+td_el.id+'", sub_id="'+repl_a.id+'")');
        td_el.replaceChild(repl_a, sel_el)
        var repl_home = document.createElement('a');
        repl_home.setAttribute("onclick", 'on_home(td_sel_id="'+td_el.id+'")')
        repl_home.innerText = "+  ";
        repl_home.href = '#'
        repl_home.id = home_el.id;
        td_el.replaceChild(repl_home, home_el);
        let tag_el = await make_el(sel_text=sel_text, sel_id=sel_id);
        // alert('tag_el.tagname: ' + tag_el.tagName)
        if(tag_el != null){
            if(tag_el.tagName == "SELECT"){
                tag_el.setAttribute("onchange", 'on_select(td_sel_id="'+td_el.id+'", sub_id="'+tag_el.id+'")');
                td_el.appendChild(tag_el);
            }
            else if(tag_el.tagName == "A"){
                while(tag_el.tagName == 'A'){
                    var span_el = document.createElement('span')
                    span_el.innerText = ' / '
                    td_el.appendChild(span_el)
                    tag_el.setAttribute("onclick", 'on_sub(a_el_id="'+tag_el.id+'", td_sel_id="'+td_el.id+'", sub_id="'+tag_el.id+'")');
                    td_el.appendChild(tag_el);
                    tag_el = await make_el(sel_text=tag_el.id, sel_id=sel_id)
                }
                if(tag_el.tagName == 'SELECT'){
                    var span_el = document.createElement('span')
                    span_el.innerText = ' '
                    td_el.appendChild(span_el)
                    tag_el.setAttribute("onchange", 'on_select(td_sel_id="'+td_el.id+'", sub_id="'+tag_el.id+'")');
                    td_el.appendChild(tag_el);
                }
            }

        }
    }
}


function init() {
    $.ajax({
        url: "/init",
        type: "get",
        success: function(response) {

            const td_sel1 = document.getElementById("td_sel1")
            while (td_sel1.firstChild) {
                td_sel1.firstChild.remove();
                }
            var select1 = document.createElement('select');
            select1.id = "sel_1"
            select1.setAttribute("onchange", 'on_sel_id(home_id="home_1", td_sel_id="td_sel1", sel_id="sel_1")');
            

            //foreach key create option element and append to select element
            var x = 0
            for(key in response){
                var opt = document.createElement('option');
                opt.value = x;
                opt.innerText = response[key];
                if(x==0){
                    opt.selected = true
                }
                select1.appendChild(opt);
                x = x + 1
            }
            var home_1 = document.createElement('div')
            home_1.id = 'home_1'
            td_sel1.appendChild(home_1)
            td_sel1.appendChild(select1);

        },
        error: function(xhr) {
            //Do Something to handle error
        }
    });
}
