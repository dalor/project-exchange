var minlenth = 6;

$( document ).ready(function() {
    set_distanse()
    $(window).resize(function(){set_distanse()})
    $(".head .title").click(function() {
        window.location.href = "/";
    })
    $("#send_write").click(
		function(){
			send_write();
		}
	);
	$("#send_edit").click(
		function(){
			send_edit('/save');
		}
	);
	$("#send_edit_un").click(
		function(){
			send_edit('/save_un');
		}
	);
	$("#send_login").click(
		function(){
			send_login();
		}
	);
	$("#send_register").click(
		function(){
			send_register();
		}
	);
	$("#send_work").click(
		function(){
			send_work();
		}
	);
	$(".more").each(
	    function(i, obj){
	        var tr = $(obj).attr('turn');
	        $(tr).mouseover(function(){
	            $(obj).slideDown(30);
            });
            $(tr).mouseout(function(){
                $(obj).slideUp(30);
            });
	    }
	)
});

function hide_login(){
    $(".login_f").hide();
    $(".register_f").show();
}

function hide_register(){
    $(".register_f").hide();
    $(".login_f").show();
}

function set_distanse(){$(".head").css("margin-top", $('.top-head').height());}

function send_work() {
    var ss = {
        id: $("#t_id").val(),
        content: $("#text div.ql-editor").html()
    }
    
    $.ajax({
        url: '/work_s',
        type: 'post',
        dataType: 'json',
        data: ss,
        success: function(data){
            if (data['ok']){
                location.reload();
            }
            else {
                alert(data['errors']);
            }
        }
    });
}

function send_write() {
    var ss = {
        title: $("#title").val(),
        description: $("#description").val(),
        content: $(".ql-editor").html(),
        progress: $("#progress").val(),
        deadline: $("#deadline").val(),
        max_people: $("#max_people").val(),
        subject: $("#subject").val()
    }
    
    $.ajax({
        url: '/write_s',
        type: 'post',
        dataType: 'json',
        data: ss,
        success: function(data){
            if (data['ok']){
                window.location.href = document.referrer;
            }
            else {
                alert(data['errors']);
            }
        }
    });
}

function send_edit(url) {
    var ss = {
        title: $("#title").val(),
        description: $("#description").val(),
        content: $(".ql-editor").html(),
        progress: $("#progress").val(),
        deadline: $("#deadline").val(),
        max_people: $("#max_people").val(),
        subject: $("#subject").val(),
        id: $("#e_id").val()
    }
    
    $.ajax({
        url: url,
        type: 'post',
        dataType: 'json',
        data: ss,
        success: function(data){
            if (data['ok']){
                window.location.href = document.referrer;
            }
            else {
                alert(data['errors']);
            }
        }
    });
}

function send_login() {
    var ss = {
        username: $("#l_login").val(),
        password: $("#l_password").val()
    }
    $.ajax({
        url: '/log',
        type: 'post',
        dataType: 'json',
        data: ss,
        success: function(data){
            if (data['ok']){
                location.reload();
            }
            else {
                $('.l_errors').html(data['errors']);
                $('.l_errors').slideDown();
            }
        }
    });
}

function send_register() {
    
    var errs = "";
    
    if (!validateLogin($("#r_login").val())){
        errs += "Login is not valid <br>";
    }
    else if($("#r_login").val().length == 0) {
        errs += "Login is empty <br>";
    }
    else if ($("#r_login").val().length < minlenth){
        errs += "Login is too short <br>";
    }
    
    if ($("#r_email").val().length == 0){
        errs += "E-mail is empty <br>";
    }
    else if (!validateEmail($("#r_email").val())){
        errs += "Change your mail <br>";
    }
    
    if($("#r_password").val().length == 0) {
        errs += "Password is empty <br>";
    }
    else if ($("#r_password").val().length < minlenth){
        errs += "Password is too short <br>";
    }
    else if ($("#r_password").val() != $("#r_r_password").val()){
        errs += "Passwords are not simililar <br>";
    }
    
    if (errs != ""){
        $('.r_errors').html(errs);
        $('.r_errors').slideDown();
        return 0;
    }
    
    $('.r_errors').hide();
    
    var ss = {
        username: $("#r_login").val(),
        password: $("#r_password").val(),
        email: $("#r_email").val(),
        name: $("#r_name").val(),
        type: $("#r_type").val()
    }
    
    $.ajax({
        url: '/reg',
        type: 'post',
        dataType: 'json',
        data: ss,
        success: function(data){
            if (data['ok']){
                alert("Check your e-mail");
                location.reload();
            }
            else {
                $('.r_errors').html(data['errors']);
                $('.r_errors').slideDown();
            }
        }
    });
}

function validateLogin(login) {
    var english = /^[A-Za-z0-9]*$/;
    return english.test(login);
}

function validateEmail(email) {
  var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(email);
}

function delete_p(id) {
    if (confirm("Are you sure to delete?")){
        $.get("/del/"+id, function(){ location.reload(); });
    }
}

function goto(id) {
    if (confirm("Are you sure get this task?")){
        $.get("/work/"+id, function(data){
            if (data.ok){
               location.reload();
            }
            else{
                alert(data.errors);
            }
        }, "json");
    }
}

function delete_un(id) {
    if (confirm("Are you sure to delete?")){
        $.get("/del_un/"+id, function(){ location.reload(); });
    }
}

function publish(id) {
    if (confirm("Are you sure to publish?")){
        $.get("/aprove/"+id, function(){ location.reload(); });
    }
}

function edit(){
    var quill = new Quill('#text', {
    modules: {
        imageResize: {
            modules: [ 'Resize', 'DisplaySize']
        },
        toolbar: [
            [{ header: [1, 2, false] }],
            ['bold', 'italic', 'underline', { 'align': [] }, { 'color': [] }],
            ['link', 'blockquote', 'code-block', 'image'],
            [{ list: 'ordered' }, { list: 'bullet' }]
                ]
        },
    theme: 'snow',
    placeholder: 'Write something...'
    });
}

function set_edit(el){
    var quill = new Quill(el, {
        modules: {
            toolbar: false
        },
        theme: 'snow'
    });
    quill.disable();
}