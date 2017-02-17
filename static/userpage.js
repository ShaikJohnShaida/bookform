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
//    $("#booklist").click(function(event) {
//        $.ajax({
//        url: "/get_book",
//        type: 'GET',
//        success:function(response){
//            var data = JSON.parse(this.responseText)
//            bookdata=data["Books"]
//            bookdata.forEach(function(o){
//                //console.log(o);
//                var elm = document.getElementById("book");
//                elm.innerHTML = elm.innerHTML + "<li>" + o.bookname+ "</li>";
//                console.log(o.bookname)
//        document.getElementById("myDropdown").classList.toggle("show");
//
//    });
//    },
//    error:function(error){
//        console.log(error);
//    }
//    });
//    });

function book() {
   var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var data = JSON.parse(this.responseText)
           bookdata=data["Books"]

            bookdata.forEach(function(o){
                console.log(o);
                var elm = document.getElementById("book");
               elm.innerHTML = elm.innerHTML + "<ul>" + o.bookname+ "</ul>";
               document.getElementById("myDropdown").classList.toggle("show");
            })
        }
    }
 xhttp.open("GET", "/get_book", true);
 xhttp.send();
}
