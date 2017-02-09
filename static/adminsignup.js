$(document).ready(function(){
    $("#adminsignup").click(function(){
         var password=$("#password").val();
         var cpassword=$("#acpassword").val();
         if(password=cpassword){
            $.ajax({
            url: '/signedup',
            data: {"password":password},
            type: 'POST',
            success:function(response){
               console.log(response);
               window.location='/userpage';
               $("#admin_signup_flash").html(response.result);
//               alert(response.result);
               },
             error:function(error){
//                console.log(error);
             },
         });
         }
    else{
        alert("password did not matched try again");
    }
    });
    });