from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify,make_response
from google.appengine.ext import deferred
from google.appengine.api import mail
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from urllib import urlencode
from google.appengine.datastore.datastore_query import Cursor
import logging

import config
import json


import logging
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
from datetime import *
import pytz
from functools import wraps
from models.bookformndbfiles import *
log = logging.getLogger(__name__)
app = Flask(__name__)
app.secret_key = os.urandom(24)

CLIENT_ID = '640513924978-autrjpeda6a4j8rgjccbpd2mt6crq7rs.apps.googleusercontent.com'
CLIENT_SECRET = 'UiGRMX5K1bUQwnlwibX8IioQ'  # Read from a file or environmental variable in a real app
SCOPE = 'https://www.googleapis.com/auth/userinfo.profile email'
REDIRECT_URI =  'https://onlinebookform.appspot.com/googledetail'

USER_PROFILE_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'

urlfetch.set_default_fetch_deadline(45)

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('homepage'))

    return wrap

@app.route('/googlelogin')
def index():
    if 'credentials' not in session:
        return redirect(url_for('googledetail'))
    credentials = json.loads(session['credentials'])
    if credentials['expires_in'] <= 0:
        return redirect(url_for('googledetail'))
    else:
        headers = {'Authorization': 'Bearer {}'.format(credentials['access_token'])}
        # req_uri = 'https://www.googleapis.com/oauth2/v1/userinfo?`'
        r = urlfetch.fetch(USER_PROFILE_URL, headers=headers, method=urlfetch.GET)
        # return json.loads(r.content).get("name")
        user = json.loads(r.content)
        session['logged_in'] = True
        session['user_email'] = user.get('email')
        session['username'] = user.get('name')
        mail = user.get('email')
        if UserDetails.query(UserDetails.email_ID == mail).get():
            return redirect(url_for('userpage'))
        UserDetails(userName = user.get("name"), email_ID = user.get("email") ).put()
        return redirect(url_for('userpage'))


@app.route('/googledetail')
def googledetail():
    if 'code' not in request.args:
        auth_uri = ('https://accounts.google.com/o/oauth2/v2/auth?response_type=code'
                    '&client_id={}&redirect_uri={}&scope={}').format(CLIENT_ID, REDIRECT_URI, SCOPE)
        log.info(auth_uri)
        return redirect(auth_uri)

    else:
        auth_code = request.args.get('code')
        log.info(auth_code)
        data = {'code': auth_code,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uri': REDIRECT_URI,
                'grant_type': 'authorization_code'}

        log.info(json.dumps(data))
        url = 'https://www.googleapis.com/oauth2/v4/token'
        header = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = urlfetch.fetch(url, method=urlfetch.POST, payload=urlencode(data), headers=header )
        log.info(r.content)
        session['credentials'] = r.content

        # json_response = json.loads(r.content)
        # userinfo = flask.request.get(json_response)
        # user = UserDetails()
        # user.put()
        # return r.content
        return redirect(url_for('index'))


def userdetails():
        pwd = request.form['pswd']
        user_details = UserDetails(
            userName=request.form['uname'],
            email_ID=request.form['email'],
            password=generate_password_hash(pwd)

        )
        user_details.put()


def newbook_request_mailing(to_user, name, book):
    sender ='jshaida786@gmail.com'
    subject_to_user = "Book Request acknowledgement"
    mailbody_to_user = '%s Book has been requested successfully. Thank you for requesting book on Book Forms.' % (book)
    mail.send_mail(sender, to_user, subject_to_user, mailbody_to_user)
    to_admin = sender
    subject_to_admin ='You have a new Book Request'
    mailbody_to_admin = '%s from %s has requested for %s book to be added to the list. Please acknowledge and add the book to the list' % (name, to_user, book)
    mail.send_mail(sender, to_admin, subject_to_admin, mailbody_to_admin)


def readbook_request_mailing(books):
    book = books
    sender = str('jshaida786@gmail.com')
    rec = session['user_email']
    receiver = rec
    subject = str('New Read Book Requested')
    body = str('Your request to read book %s has been submitted successfully.' % (book))
    mail.send_mail(sender, receiver, subject, body)
    receiver = sender
    subject_to_admin = str('New Read Book Requested')
    nm = session['username']
    name = nm
    body_to_admin = str('%s from %s has been requested to read %s.' % (name, receiver, book))
    mail.send_mail(sender, receiver, subject_to_admin, body_to_admin)


@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/loginpage', methods = ['POST'])
def loginpage():
    username = request.form['name']
    pswd = request.form['password']
    if UserDetails.query(UserDetails.email_ID == username).get():
        user = UserDetails.query(UserDetails.email_ID == username).get()
        if check_password_hash(user.password, pswd):
            session['logged_in'] = True
            session['user_email'] = username
            session['username'] = user.userName
            data=''
            return jsonify(result=data)
        else:
            data='Invalid username or password.'
            return jsonify(result=data)
    else:
        data='Invalid user credentials.'
        return jsonify(result=data)


@app.route('/userpage')
@login_required
def userpage():
    books = Books.query().fetch()
    return render_template('userpage.html', book=books)


@app.route('/userlogout')
def userlogout():
    session.pop('user_email', None)
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('homepage'))


@app.route('/bookrequest', methods=['POST'])
def bookrequest():
    book = request.form['bookname']
    author = request.form['authorname']
    if Books.query(Books.name==book).get():
        if Books.query(Books.author==author).get():
            data="the book which you requested is already in the book list"
            return jsonify(result=data)
    user_email = session['user_email']
    name = session['username']
    newbook_request_mailing(user_email, name, book)
    data='Book requested successfully'
    return jsonify(result=data)


@app.route('/bookread', methods=['POST'])
def bookread():
    book=request.form['options']
    # deferred.defer(readbook_request_mailing,book)
    # logging.info(book)
    readbook_request_mailing(book)
    flash('Your book will be sent to you shortly.')
    return redirect(url_for('userpage'))

@app.route('/signup', methods=['POST'])
def signup():
    userset = UserDetails.query().fetch()
    for user in userset:
        if user.email_ID == request.form['email']:
            data= 'Email ID you entered has already been signed up'
            return jsonify(result=data)
            # return redirect(url_for('homepage'))
        else:
            continue
    else:
        userdetails()
        data= 'Signed up successfully. Log in to access your account in BookForm'
        return jsonify(result=data)


@app.route('/adminsignup')
def adminsignup():
    if Admins.query(Admins.email == session['user_email']).get():

        data = 'You are already an Admin on BookForms.'
        return jsonify(result=data)
    else:
        data = ''
        return jsonify(result=data)
    # return render_template('adminsignup.9html')

@app.route('/admin_signup_page')
def admin_signup_page():
    return render_template('adminsignup.html')
# @app.route('/adminrequest')
# def adminrequest():
#     sender = str('jshaida786@gmail.com')
#     to = str(session['user_email'])
#     subject = str('Make me as a Admin')
#     body = str('Click this link and fill up the admin signup form. \n https://http://onlinebookform.appspot.com/adminsignup')
#     mail.send_mail(sender, to, subject, body)
#     flash('Check out your email to get the link for admin form.')
#     return redirect(url_for('userpage'))

@login_required
@app.route('/signedup', methods=['POST'])
def signedup():
    # if request.form['adminpassword'] == request.form['confirmpassword']:
    #     if UserDetails.query(UserDetails.email_ID == request.form['adminemail']).get():
            pw = request.form['password']
            admins = Admins(
                username=session['username'],
                email= session['user_email'],
                password=generate_password_hash(pw)
            )
            admins.put()
            data='Signed up successfully'
            return  jsonify(result=data)
    #     else:
    #         flash('You are not a user on BookForms. Only users of BookForms can become Admin on BookForms')
    #         return redirect(url_for('adminsignup'))
    # flash('Passwords do not match')
    # return redirect(url_for('adminsignup'))

@app.route('/forgot')
def forgot():
    return render_template('forgotpassword.html')


@app.route('/forgotpassword',methods=['POST'])
def forgotpassword():
    mailid=request.form['mail']
    uid=str(uuid.uuid4())
    utc = pytz.UTC
    timestamp= datetime.now().replace(tzinfo=utc)
    timestamp=timestamp.time()

    confirmation= ForgotPassword(id=mailid,email=mailid,uid=uid,timestamp=timestamp)
    confirmation.put()

    link = 'https://onlinebookform.appspot.com/resetpassword/{}&id={}'.format(uid,mailid)

    send_email(to=mailid, body=link)
    flash('Reset Password Link has been sent to your Email,Please check within 10 mins')
    return redirect(url_for('homepage'))




def send_email(to, body, sender='jshaida786@gmail.com'):
        subject = 'Reset Password Request - Bookforms'
        mail.send_mail(sender, to, subject, body)



@app.route('/resetpassword/<uid>&<mailid>')
def resetpassword(uid,mailid):

    logging.info(uid)
    uid=uid
    id=mailid
    logging.info(id)
    #key_parent = ndb.Key('ForgotPasswordParent', 'uid_parent').get()
    uid_key=ForgotPassword.query(ForgotPassword.uid==uid).get()
    #,parent=key_parent)

    logging.info(uid_key)
    timestamp=uid_key.timestamp
    logging.info(timestamp)
    utc = pytz.UTC
    currenttime = datetime.now().replace(tzinfo=utc)
    currenttime = currenttime.time()
    logging.info(currenttime)
    if timestamp.hour == currenttime.hour:
        minutedifference = currenttime.minute - timestamp.minute
        logging.info(minutedifference)
        if minutedifference <= 10:
            return render_template('resetpassword.html', uid=uid)
        else:
            return 'session expired'
    else:
        return 'session expired'


# @app.route('/resetpasswords/<uid>')
# def resetpasswords(uid):
#     uid=uid
#     return render_template('resetpaswword.html',uid)



@app.route('/resetpasswordstore',methods=['POST'])
def resetpasswordstore():
     mail= request.form['mail']
     uid=request.form['uid']
     entity_key=ForgotPassword.query(ForgotPassword.email == mail).get()
     logging.info(entity_key)
     originaluid=entity_key.uid

     if uid == originaluid:
         if request.form['password'] == request.form['reenterpassword']:
             user=UserDetails.query(UserDetails.email_ID == mail).get()
             logging.info(user)
             newpassword=request.form['password']
             newpassword=generate_password_hash(newpassword)
             user.password = newpassword
             logging.info(user.password)
             user.put()
             flash('Password reset Sucessfully')
             return redirect(url_for('homepage'))

         else:
             return 'Type correct password'

     else:
         return 'Don\'t try to change the uid'




@app.route('/adminlogin', methods=['POST'])
def adminlogin():
    adminName = request.form['name']
    adminPsw = request.form['password']
    if Admins.query(Admins.email == adminName).get():
        admin = Admins.query(Admins.email == adminName).get()
        #the admin entity contain all data base of particular admin user

        if check_password_hash(admin.password, adminPsw):
            session['logged_in'] = True
            return jsonify(result = "")
        else:
            data = "Invalid Email or password."
            return jsonify(result = data)
    else:
        data = "Invalid admin credentials."
        return jsonify(result = data)

@app.route('/adminpage')
@login_required
def adminpage():
    return render_template('adminpage.html')


@app.route('/addingbook', methods=['POST'])
def addingbook():
    name = request.form['bookname']
    genre = request.form['gener']
    author = request.form['authorname']
    if Books.query(Books.name==name,Books.genre==genre,Books.author==author).get():
        data="Book already in the list"
        return jsonify(result=data)
    else:
        addbook = Books(name=name, genre=genre, author=author)
        addbook.put()
        data= "Book added successfully"
        return jsonify(result = data)

@app.route('/get_book')
def get_book():
# data = json.dumps({'isDown': 'Nope'})
# return data, 200, {'Content-Type': 'application/json'}
    books=Books.query().fetch()
    logging.info(books)
    dict=[]
    for book in books:
        dict.append({"id":book.key.id(),"bookname":book.name,"author":book.author,"gener":book.genre})
    bookdata = json.dumps({"Books":dict})

    logging.info(bookdata)
    headers = {'Content-Type': 'application/json'}
    return bookdata,200,headers

@app.route('/adminlogout')
def adminlogout():
    session.pop('logged_in', None)
    return redirect(url_for('homepage'))


datalimit = 2
mykey = 'thisismykey'

# @app.route('/get_books')
# def get_books():
#     if mykey == request.headers.get('key'):
#         cursor = Cursor(urlsafe = request.args.get('cursor'))
#         data, next_cursor, more = Books.query().fetch_page(datalimit, start_cursor=cursor)
#         dic = []
#         for book in data:
#             a = book.key.id()
#             dic.append({"id":a,'name': book.name, 'genre': book.genre, 'author': book.author})
#         if more or next_cursor:
#             book = {'books': dic, "cursor": next_cursor.urlsafe(), "more": more}
#             return jsonify(book)
#     else:
#        return make_response(jsonify({'error': 'Invalid secret_key given by you'}), 404)

# @app.route('/Books', methods=['POST'])
# def restapiaddingbooks():
#     if mykey != request.headers.get('key'):
#         return make_response(jsonify({'error':'Invalid yor authorized key'}),404)
#     else:
#         data = request.get_json()
#         bookname = data.get('name')
#         bookauthor = data.get('author')
#         bookgenre = data.get('genre')
#         if Books.query(ndb.AND(Books.name == bookname, Books.author == bookauthor)).get():
#             return make_response(jsonify({'result': 'This book is already in the list'}), 200)
#         else:
#             books = Books(name=bookname, genre=bookgenre, author=bookauthor)
#             books.put()
#             logging.info(books)
#             return make_response(jsonify({'result': 'Your book added successfully'}), 200)

@app.route('/bookdel', methods=['DELETE'])
def bookdel():

    if mykey != request.headers.get('key'):
        return make_response(jsonify({'error': 'Invalid yor authorized key'}), 404)

    else:
        bookname=request.args.get('bookname')
        logging.info(bookname)
        if Books.query(Books.name==bookname).get():
            book=Books.query(Books.name == bookname).get()
            book.key.delete()
            return make_response(jsonify({"result":"Book deleted sucessfully"}))
            # logging.info("deleted the book")
        # data=request.get_json()
        # bookname = data.get('name')
        # bookauthor = data.get('author')
        # bookgenre = data.get('genre')
        # if Books.query(ndb.AND(Books.name == bookname, Books.author == bookauthor)).get():
        #    book =Books.query(ndb.AND(Books.name == bookname, Books.author == bookauthor)).get()
        #     key = book.key()

@app.route('/apiupdate')
def apiupdate():
    url = 'http://localhost:8080/restapiaddingbooks'
    data = {"name":"brain rules", "author": "john", "genre": "knowledge"}
    header = {'key': 'thisismykey', 'Content-Type': 'application/json'}
    r = urlfetch.fetch(url, headers=header, method=urlfetch.POST, payload=json.dumps(data))
    return r.content

@app.route('/apireceive')
def apireceive():
        url = 'http://localhost:8080/get_books'
        header = {'key': 'thisismykey'}
        r = urlfetch.fetch(url, headers=header)
        return r.content
# rest api request with optioanl parameters
@app.route('/Book')
def filterbook():
    if mykey!=request.headers.get('key'):
        return make_response(jsonify({'error':"Invalid yor authorized key"}))
    else:
        bookname =request.args.get('name')
        authorname = request.args.get('author')
        genre = request.args.get('genre')
        limit = request.args.get('limit') or 2
        cursor = Cursor(urlsafe=request.args.get('cursor'))
        if not bookname and not authorname and not genre:
            data, next_cursor, more = Books.query().fetch_page(int(limit), start_cursor=cursor)
        elif not bookname and not authorname and genre :
            data, next_cursor, more = Books.query(Books.genre==genre).fetch_page(int(limit), start_cursor=cursor)
        elif not bookname and not genre and authorname:
            data, next_cursor, more = Books.query(Books.author == authorname).fetch_page(int(limit), start_cursor=cursor)
        elif bookname and not authorname and not genre:
            data, next_cursor, more = Books.query(Books.name == bookname).fetch_page(int(limit), start_cursor=cursor)
        elif not bookname and authorname and genre:
            logging.info('true')
            data, next_cursor, more = Books.query(Books.author == authorname, Books.genre == genre).fetch_page(int(limit), start_cursor=cursor)
        elif bookname and genre and not authorname:
            data, next_cursor, more = Books.query(Books.name == bookname, Books.genre == genre).fetch_page(int(limit), start_cursor=cursor)
        elif bookname and authorname and not genre:
            data, next_cursor, more = Books.query(Books.author == authorname,Books.name == bookname).fetch_page(int(limit), start_cursor=cursor)
        else:
            data, next_cursor, more = Books.query(Books.name==bookname, Books.author == authorname,Books.genre==genre).fetch_page(int(limit), start_cursor=cursor)
        dic = []
        for book in data:
            dic.append({"id": book.key.id(), 'name': book.name, 'genre': book.genre, 'author': book.author})
        if more or next_cursor:
            book = {'books': dic, "cursor": next_cursor.urlsafe(), "more": more}
            return jsonify(book)

@app.route('/Book', methods=['POST'])
def book():
    if mykey !=request.headers.get('key'):
        return make_response(jsonify({'error': 'Invalid yor authorized key'}), 404)
    else:
        data = request.get_json()
        bookname = data.get('name')
        bookauthor = data.get('author')
        bookgenre = data.get('genre')
        book = Books.query(Books.name == bookname, Books.author == bookauthor, Books.genre == bookgenre).get()
        if book:
            return make_response(jsonify({'result': 'This book is already in the list',"bookid":book.key.id()}), 200)
        else:
            books = Books(name=bookname, genre=bookgenre, author=bookauthor)
            books.put()
            return make_response(jsonify({'result': 'Your book added successfully','book id': books.key.id()}), 200)


@app.route('/Book/<bookID>',methods = ['PUT'])
def bookupdate(bookID):
    if mykey !=request.headers.get('key'):
        return make_response(jsonify({'error': 'Invalid yor authorized key'}), 404)
    else:
        data = request.get_json()
        bookname = data.get('name')
        bookauthor = data.get('author')
        bookgenre = data.get('genre')
        mybook = Books.get_by_id(int(bookID))
        logging.info(mybook)
        mybook.name=bookname
        mybook.author=bookauthor
        mybook.genre=bookgenre
        mybook.put()
        return make_response(jsonify({"result" : "Book successfully updated with given id",'bookid':mybook.key.id()}))


@app.route('/Book/<bookID>',methods = ['DELETE'])
def bookdelete(bookID):
    if mykey !=request.headers.get('key'):
        return make_response(jsonify({'error': 'Invalid yor authorized key',"id":bookID}), 404)
    else:
        book=Books.get_by_id(int(bookID))
        book.key.delete()
        return make_response(jsonify({"result" : "Book Successfully deleted with givn id",'bookid':bookID}))

@app.route('/requestbook',methods = ['POST'])
def request_book():
    if mykey != request.headers.get('key'):
        return make_response(jsonify({'error': 'Invalid yor authorized key'}), 404)
    else:
        data = request.get_json()
        bookname = data.get('name')
        bookauthor = data.get('author')
        bookgenre = data.get('genre')
        newbook = Books(name = bookname , author = bookauthor, genre= bookgenre)
        newbook.put()
        bookid=newbook.key.id()
        return make_response(jsonify({"result" : " The Requested Book is Successfully added",'bookid':newbook.key.id()}))
@app.route("/sample")
def sample():
    bookname = request.args.get('name')
    authorname = request.args.get('author')
    genre = request.args.get('genre')
    limit = request.args.get('limit') or 2
    cursor = Cursor(urlsafe=request.args.get('cursor'))
    logging.info('authorname : {} limit : {}'.format(authorname, int(limit)))
    query = Books.query()
    if bookname:
        query = query.filter(Books.name == bookname)
    if authorname:
        query = query.filter(Books.author == authorname )
    if genre:
        query = query.filter(Books.genre == genre)
    data,next_cursor,more = query.fetch_page(int(limit), start_cursor=cursor)
    logging.info(data)
    dic = []
    for book in data:
        dic.append({"id": book.key.id(), 'name': book.name, 'genre': book.genre, 'author': book.author})
    if more or next_cursor:
         book = {'books': dic, "cursor": next_cursor.urlsafe(), "more": more}
         return jsonify(book)
if __name__ == '__main__':
    app.run(debug=True)