window.onload = function booklist() {
   var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var data = JSON.parse(this.responseText)
           bookdata=data["Books"]

            bookdata.forEach(function(o){
                console.log(o);
                var elm = document.getElementById("row");
                elm.innerHTML = elm.innerHTML + "<tr id="+o.id+"><td>" +o.bookname + "</td><td><button onclick = " + "deletemybook("+ o.id + ")>delete book</button></td></tr>";
            })
        }
    }
 xhttp.open("GET", "/get_book", true);
 xhttp.send();
}

function deletemybook(bookid) {
 var bookId=bookid;
 var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {

        window.location.reload();
//           $("row").hide()
           console.log("sucess");
    }
}
xhttp.open("DELETE","/Book/"+bookId,true);
xhttp.send();
}