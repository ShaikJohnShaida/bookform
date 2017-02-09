
$(document).ready(function() {
    $('#loginbutton').click(function() {
        var name = $('#uemail').val();
        var password = $('#psw').val();
        $.ajax({
            url: '/loginpage',
            data: {"name": name, "password": password},
            type: 'POST',
//            async: true,
            success: function(response) {
                if (response.result == '') {
                      window.location="/userpage";
                }
                else {
                    console.log(response);
                $("#loginflash").html(response.result);

                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});


$(document).ready(function(){
    $("#adminlogin-button").click(function(){
    var name=$('#auname').val();
    var password=$('#apw').val();
    $.ajax({
        url:'/adminlogin',
        data:{"name":name,"password":password},
        type:'POST',
        success: function(response){
            if (response.result === '') {
            window.location="/adminpage";
            }
            else{
                console.log(response);
            $("admin_flash_message").html(response.result)
            }
            },
        error: function(error){
            console.log(error);
         }
    });
    });
});

$(document).ready(function(){
    $("#signup_button").click(function(){
    var uname=$("#uname").val();
    var email=$('#email').val();
    var pswd=$("#pswd").val();
    var rpswd=$("#rpswd").val();
    if(pswd==rpswd){
        $.ajax({
        url:'/signup',
        data:{"uname":uname, "email":email, "pswd":pswd},
        type:'POST',
//        async:true,
        success:function(response){
            console.log(response);
            $("#signupflash").html(response.result);
        },
        error: function(error){
//            console.log(error);
        }
        });
        }
    else{
           alert('password do not match');
     }
        });
    });


