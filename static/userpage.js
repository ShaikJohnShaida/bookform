$(document).ready(function(){
    $("#request").click(function(){
    var bookname =$("#bookname").val();
    var authorname=$("#authorname").val();
    if(bookname=='' || authorname=='')
    {
    alert("please add enter book name and author name");
    }
    else{
    $.ajax({
        url:"/bookrequest",
        data:{"bookname":bookname,"authorname":authorname},
        type:'POST',
    success: function(response){
        console.log(response);
         $("#flash").html(response.result);
    },
    error:function(error){
        console.log(error);
    },
    });
    }
    });
//   # });
    $("#adminlink").click(function(event){
        $.ajax({
        url:"/adminsignup",
        type:'GET',
        success:function(response){
            if(response.result === ''){
                console.log(response);
                window.location="/admin_signup_page";
            }
            else{
                console.log(response);
                $("#adminrequestflash").html(response.result);
            }
        },

        error:function(error){
            console.log(error);
        },
        });
        event.preventDefault();

        });
        });