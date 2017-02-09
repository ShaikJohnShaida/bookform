$(document).ready(function(){
    $("#boook_adding").click(function(){
        var bookname=$("#bookname").val();
        var gener=$("#gener").val();
        var authorname=$("#authorname").val();
        if(bookname==="" || gener==="" || authorname==="")
            {
            alert("please enter valid names don't leaven the fields empty");
            }
        else{
            $.ajax({
            url:"/addingbook",
            data:{"bookname": bookname,"gener": gener,"authorname": authorname},
            type:'POST',
            success:function(response){
                console.log(response);
                $("#adminpageflash").html(response.result);
            },
            error:function(error){
                console.log(error);
            }
        });
    }
});
});

