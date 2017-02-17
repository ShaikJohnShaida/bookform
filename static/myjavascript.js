// Get the modal
var modal1 = document.getElementById('id01');
var modal2= document.getElementById('id02');
var modal3= document.getElementById('id03');

//// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal1) {
        modal.style.display = "none";
    }
    if (event.target == modal2) {
        modal.style.display = "none";
    }
    if (event.target == modal3) {
        modal.style.display = "none";
    }

}
function Validate() {
       var password = document.getElementById("pswd").value;
        var confirmPassword = document.getElementById("rpswd").value;
        if (password != confirmPassword) {
            alert("Passwords do not match.");
            return false;
        }
       return true;
}

function booklist() {
   var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var data = JSON.parse(this.responseText)
           bookdata=data["Books"]

            bookdata.forEach(function(o){
                console.log(o);
                var elm = document.getElementById("options");
               elm.innerHTML = elm.innerHTML + "<option>" + o.bookname+ "</option>";
            })
        }
    }
 xhttp.open("GET", "/get_book", true);
 xhttp.send();
}

//$("#booklist").click(function(event){
//$.ajax({
//    url: "/get_book",
//    type: 'GET',
//    success:function(response){
//     var data = JSON.parse(this.responseText)
//           bookdata=data["Books"]

//            bookdata.forEach(function(o){
//                console.log(o);
//                var elm = document.getElementById("booklist");
//               elm.innerHTML = elm.innerHTML + "<li>" + o.bookname+ "</li>";
//    }
//    },
//    error:function(error){
//        console.log(error);
//    }
//});
//}
