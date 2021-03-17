######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
from datetime import datetime


#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '13886003474'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email from Users")
    return cursor.fetchall()

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not(email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not(email) or email not in str(users):
        return
    user = User()
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0] )
    if request.form['password'] == pwd:
        user.id = email
        return user
    return None

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
    return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'></input>
                <input type='password' name='password' id='password' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form></br>
           <a href='/'>Home</a>
               '''
    #The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    #check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0] )
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user) #okay login in user
            return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

    #information did not match
    return "<a href='/login'>Try again</a>\
            </br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
    flask_login.logout_user()
    userlist = getTopUsers()
    return render_template('hello.html', message='Logged out',userlist=userlist)

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', supress=True)

@app.route("/register", methods=['POST'])
def register_user():
    try:
        email=request.form.get('email')
        password=request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        hometown = request.form.get('hometown')
        gender = request.form.get('gender')
        DOB = request.form.get('DOB')
    except:
        print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test =  isEmailUnique(email)
    if test:
        print(cursor.execute("INSERT INTO Users (email, password,first_name,last_name,hometown,gender, DOB) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}','{6}')".format(email, password,first_name,last_name,hometown,gender, DOB)))
        conn.commit()
        #log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        userlist = getTopUsers()
        return render_template('hello.html', name=first_name, message='Account Created!',userlist=userlist)
    else:
        return render_template('register.html', supress=False)

def getUsersName(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT first_name FROM Users WHERE uid = '{0}'".format(uid))
    return cursor.fetchone()[0]

def getUserFriend(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT fuid FROM Friends_Is_Friend WHERE uid = '{0}'".format(uid))
    return cursor.fetchall()

def getUsersAlbums(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT aid, name, DOC FROM Albums WHERE uid = '{0}'".format(uid))
    return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getUserContribution(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT contribution FROM Users WHERE uid = '{0}'".format(uid))
    return cursor.fetchone()[0]

def getAlbumName(aid):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Albums WHERE aid ='{0}'".format(aid))
    return cursor.fetchone()[0]

def getAlbumOwner(aid):
    cursor=conn.cursor()
    cursor.execute("SELECT uid FROM Albums WHERE aid ='{0}'".format(aid))
    return cursor.fetchone()

def getPhotoOwner(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT uid FROM Photos WHERE pid ='{0}'".format(pid))
    return cursor.fetchone()[0]

def getPhotoComment(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT comment, date, pid, aid,uid,uname FROM Comments_Leaves_Has WHERE pid ='{0}'".format(pid))
    return cursor.fetchall()

def getAlbumPhotos(aid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, pid, caption,aid FROM Photos WHERE aid ='{0}'".format(aid))
    return cursor.fetchall()

def getAlbumComments(aid):
    cursor = conn.cursor()
    cursor.execute("SELECT comment, date, pid, aid,uid,uname FROM Comments_Leaves_Has WHERE aid ='{0}'".format(aid))
    return cursor.fetchall()

def getAlbumId(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT aid FROM Photos WHERE pid ='{0}'".format(pid))
    return cursor.fetchone()[0]

def getUsersPhotos(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, pid, caption FROM Photos WHERE uid = '{0}'".format(uid))
    return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getPhoto(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, pid, caption, uid FROM Photos WHERE pid = '{0}'".format(pid))
    return cursor.fetchone()

def getPhotoTag(pid):
    cursor=conn.cursor()
    cursor.execute("SELECT description,pid,uid FROM Tags_Associates WHERE pid = '{0}'".format(pid))
    return cursor.fetchall()

def getPhotoByTag(description):
    cursor = conn.cursor()
    cursor.execute("SELECT description,pid,uid FROM Tags_Associates WHERE description= '{0}'".format(description))
    return cursor.fetchall()

def getAllPhotos():
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT uid FROM Photos")
    uidlist = cursor.fetchall()
    users=[]
    for uid in uidlist:
        users.append([uid[0],getUsersName(uid[0])])
    for j in range(0,len(users)):
        #[(uid,firstname),[(aid,name)]]
        albums=getUsersAlbums(users[j][0])
        for z in range(0,len(albums)):
            aid=albums[z][0]
            aname =albums[z][1]
            users[j].append([])
            users[j][2].append([aid,aname,[],[]])
            comments = getAlbumComments(aid)
            for i in range(0,len(comments)):
                users[j][2][z][3].append(comments[i])
            photos=getAlbumPhotos(aid)
            for i in range(0,len(photos)):
                pid=photos[i][1]
                if pid == -1:
                    continue
                numlikes = getNumLikes(photos[i][1])
                tags = getPhotoTag(pid)
                users[j][2][z][2].append([photos[i], numlikes,tags])
    return users

def getNumLikes(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Liked_By WHERE pid='{0}'".format(pid))
    return cursor.fetchone()[0]  # NOTE list of tuples, [(description, pid), ...]

def getTopUsers():
    cursor = conn.cursor()
    cursor.execute(
        "SELECT first_name, last_name, email, contribution FROM Users ORDER BY contribution DESC LIMIT 10")
    return cursor.fetchall()

def getAllTags():
    cursor = conn.cursor()
    cursor.execute("SELECT description, count(pid) as count FROM Tags_Associates GROUP BY description ORDER BY count DESC")
    return cursor.fetchall()  # NOTE list of tuples, [(description, pid), ...]

def getTopMyTags(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT description, count(pid) as count FROM Tags_Associates WHERE uid='{0}' GROUP BY description ORDER BY count DESC LIMIT 5".format(uid))
    return cursor.fetchall()

def getMyTags(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT description, pid FROM Tags_Associates WHERE  uid = '{0}'".format(uid))
    return cursor.fetchall()  # NOTE list of tuples, [(description, pid), ...]

def getTagsPhotosAll(description):
    cursor = conn.cursor()
    cursor.execute("SELECT description, pid FROM Tags_Associates WHERE description = '{0}'".format(description))
    return cursor.fetchall()  # NOTE list of tuples, [(description, pid), ...]

def getTagsPhotosMy(description,uid):
    cursor = conn.cursor()
    cursor.execute("SELECT description, pid FROM Tags_Associates WHERE description = '{0}' AND uid = '{1}'".format(description,uid))
    return cursor.fetchall()  # NOTE list of tuples, [(description, pid), ...]

def getRecommandFriend(uid):
    cursor=conn.cursor()
    cursor.execute("SELECT fuid FROM Friends_Is_Friend WHERE uid ='{0}' ".format(uid))
    result = cursor.fetchall()
    friendlist = []
    for f in result:
        cursor.execute("SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE uid ='{0}' ".
                       format(f[0]))
        friendlist.append(cursor.fetchone())
    count = {}
    for f in result:
        fuid = f[0]
        ff = getUserFriend(fuid)
        for stranger in ff:
            if stranger[0] == uid:
                continue
            if stranger not in result and stranger[0] not in count:
                count[stranger[0]] = 1
            elif stranger not in result:
                count[stranger[0]] = count[stranger[0]] + 1
    recommand = []
    count = sorted(count.items(), key=lambda item: item[1], reverse=True)
    for fuid in count:
        if fuid[1] != 0:
            cursor.execute(
                "SELECT first_name, last_name, email, DOB, hometown, gender, uid FROM Users WHERE uid ='{0}' ".
                    format(fuid[0]))
            user = cursor.fetchone()
            recommand.append([user, fuid[1]])
    return recommand

def getLikedPhotos(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT pid  FROM Liked_By WHERE uid = '{0}'".format(uid))
    photos = cursor.fetchall()
    result=[]
    for photo in photos:
        result.append(photo[0])
    return result

def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT uid  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

def isEmailUnique(email):
    #use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
        #this means there are greater than zero entries with that email
        return False
    else:
        return True
#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    userlist = getTopUsers()
    return render_template('hello.html', name=getUsersName(uid), message="Here's your profile",userlist=userlist)

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        aid = request.form.get('aid')
        uid = getUserIdFromEmail(flask_login.current_user.id)
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        newtag = request.form.get('newtag')
        newtag = newtag.lower()
        if newtag:
            if newtag[len(newtag)-1] == ";":
                newtag=newtag[:-1]
        newtags=newtag.split(";")
        newtags=list(dict.fromkeys(newtags))
        choosedtags = request.form.getlist('choosetag')
        photo_data =imgfile.read()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Photos (imgdata,aid, uid, caption) VALUES (%s, %s, %s, %s )''' ,(photo_data, aid, uid, caption))
        newcontribution = getUserContribution(uid) + 1
        cursor.execute("UPDATE Users SET contribution='{1}'  WHERE uid = '{0}'".format(uid,newcontribution))
        conn.commit()
        cursor.execute("SELECT pid FROM Photos ORDER BY pid DESC LIMIT 1;")
        pid = cursor.fetchone()[0]

        if newtags!=[''] and newtags!=[""] and newtags!=None and newtags!=[]:
            for tag in newtags:
                choosedtags.append(tag)
        choosedtags = list(dict.fromkeys(choosedtags))
        if choosedtags!=[] and choosedtags!=[""]:
            for tag in choosedtags:
                if tag == '' or tag == ' ' or tag is None:
                    continue
                cursor.execute('''INSERT INTO Tags_Associates (description,pid,uid) VALUES (%s, %s, %s)''',
                        (tag, pid, uid))
        conn.commit()
        photos = getAlbumPhotos(aid)
        photolist = []
        for photo in photos:
            pid=photo[1]
            if pid == -1:
                continue
            tags=getPhotoTag(pid)
            numlikes = getNumLikes(pid)
            photolist.append([photo, numlikes,tags])
        return render_template('onealbum.html',aid=aid, name=getAlbumName(aid), message='Photo uploaded!', photos=photolist, base64=base64)
    #The method is GET so we return a  HTML form to upload the a photo.
    else:
        aid=request.args.get('aid')
        albumname= getAlbumName(aid)
        return render_template('upload.html',aid=aid,albumname=albumname,tags=getAllTags())
#end photo uploading code


@app.route("/friend", methods=['GET','POST'])
@flask_login.login_required
def searchfriend():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        hometown = request.form.get('hometown')
        cursor = conn.cursor()
        if email and first_name and last_name:
            cursor.execute("SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE email = '{0}'"
                           "AND first_name='{1}' AND last_name ='{2}'".format(email, first_name,last_name))
        elif first_name and last_name:
            cursor.execute("SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE first_name "
                           "='{first_name}' AND last_name ='{last_name}'".format(first_name=first_name,
                                                                                 last_name=last_name))
        elif first_name:
            cursor.execute("SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE first_name "
                           "='{first_name}'".format(first_name=first_name))
        elif last_name:
            cursor.execute("SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE last_name "
                           "='{last_name}'".format(last_name=last_name))
        elif email:
            cursor.execute("SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE email = '{0}'"
                           .format(email))
        elif hometown:
            cursor.execute(
                "SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE hometown = '{0}'".format(
                    hometown))
        search = cursor.fetchall()
        searchlist=[]
        if search:
            for temp in search:
                if temp[2] != 'anonymous@bu.edu':
                    searchlist.append(temp)
        recommand = getRecommandFriend(uid)
        if searchlist:
            return render_template('friend.html', searchlist=searchlist, recommand=recommand,friendlist=friendlist)
        else:
            return render_template('friend.html', searchlist=None, recommand=recommand,friendlist=friendlist)
    else:
        uid = getUserIdFromEmail(flask_login.current_user.id)
        friendlist = []
        cursor = conn.cursor()
        cursor.execute("SELECT fuid FROM Friends_Is_Friend WHERE uid ='{0}' ".format(uid))
        result = cursor.fetchall()
        for f in result:
            cursor.execute("SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE uid ='{0}' ".
                           format(f[0]))
            friendlist.append(cursor.fetchone())
        recommand = getRecommandFriend(uid)
        return render_template('friend.html',friendlist=friendlist,recommand=recommand)


@app.route("/addfriend", methods=['GET'])
@flask_login.login_required
def addfriend():
    if request.method == 'GET':
        femail = request.args.get('femail')
        if femail is None:
            message = "None"
            return render_template('addfriend.html', message=message)
        fuid = getUserIdFromEmail(femail)
        uid = getUserIdFromEmail(flask_login.current_user.id)
        DOF = datetime.today().strftime('%Y-%m-%d')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Friends_Is_Friend WHERE uid ='{0}' AND fuid = '{1}'".format(uid,fuid))
        count = cursor.rowcount
        if fuid == uid:
            message = "Same"
        elif count == 0 :
            message = "True"
            cursor.execute('''INSERT INTO Friends_Is_Friend (DOF, fuid, uid) VALUES (%s, %s, %s )''' ,(DOF,fuid, uid))
            cursor.execute('''INSERT INTO Friends_Is_Friend (DOF, fuid, uid) VALUES (%s, %s, %s )''', (DOF, uid, fuid))
            conn.commit()
        elif count == 1:
            message = "False"
        else:
            message = "Error"

        cursor.execute("SELECT fuid FROM Friends_Is_Friend WHERE uid ='{0}' ".format(uid))
        result = cursor.fetchall()
        friendlist =[]
        for f in result:
            cursor.execute("SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE uid ='{0}' ".
                           format(f[0]))
            friendlist.append(cursor.fetchone())
        recommand = getRecommandFriend(uid)
        return render_template('addfriend.html', message=message, friendlist=friendlist,recommand=recommand)


@app.route('/album', methods=['GET', 'POST'])
@flask_login.login_required
def create_album():
    if request.method == 'POST':
        distinction=request.form.get('distinction')
        uid = getUserIdFromEmail(flask_login.current_user.id)
        cursor = conn.cursor()
        if distinction=='0':
            uid = getUserIdFromEmail(flask_login.current_user.id)
            album_name = request.form.get('name')
            DOC = datetime.today().strftime('%Y-%m-%d')
            cursor.execute('''INSERT INTO Albums (uid, name, DOC) VALUES (%s, %s, %s )''' ,(uid,album_name, DOC))
            conn.commit()
            return render_template('album.html',album=getUsersAlbums(uid), message='Album created!')
        elif distinction=='1':
            aid=request.form.get('aid')
            name = getAlbumName(aid)
            photos=getAlbumPhotos(aid)
            comments=getAlbumComments(aid)
            for comment in comments:
                cuid=comment[4]
                newcontribution=getUserContribution(cuid) - 1
                cursor.execute("UPDATE Users SET contribution='{1}'  WHERE uid = '{0}'".format(cuid, newcontribution))
            newcontribution=getUserContribution(uid) - len(photos)
            cursor.execute("UPDATE Users SET contribution='{1}'  WHERE uid = '{0}'".format(uid, newcontribution))
            for photo in photos:
                pid=photo[1]
                cursor.execute("UPDATE Tags_Associates SET pid='-1'  WHERE pid = '{0}'".format(pid))

            cursor.execute("DELETE FROM Albums WHERE aid='{0}'".format(aid))
            conn.commit()
            string = "Album "+name+" deleted."
            return render_template('album.html', album=getUsersAlbums(uid),message=string)
        else:
            aid = request.form.get('aid')
            newname=request.form.get('newname')
            oldname = getAlbumName(aid)
            cursor.execute("UPDATE Albums SET name='{1}'  WHERE aid = '{0}'".format(aid, newname))
            conn.commit()
            string = "Album " + oldname + " renamed to "+newname+"."
            return render_template('album.html', album=getUsersAlbums(uid), message=string)


    #The method is GET so we return a  HTML form to upload the a photo.
    else:
        uid = getUserIdFromEmail(flask_login.current_user.id)
        return render_template('album.html',album=getUsersAlbums(uid))

@app.route("/onealbum", methods=['GET','POST'])
@flask_login.login_required
def onealbum():
    if request.method=='POST':
        aid = request.args.get('aid')
        pid = request.form.get('pid')
        distinction = request.form.get('distinction')
        owneruid = getAlbumOwner(aid)
        cursor = conn.cursor()
        if flask_login.current_user.is_authenticated == False:
            uid = getUserIdFromEmail("anonymous@bu.edu")
        else:
            uid = getUserIdFromEmail(flask_login.current_user.id)
        if distinction == '0':
            comment = request.form.get('comment')
            date = datetime.today().strftime('%Y-%m-%d,%H:%M:%S')
            uname = getUsersName(uid)
            cursor.execute('''INSERT INTO  Comments_Leaves_Has (comment,date, pid, aid,uid,uname) VALUES (%s, %s,%s,%s, %s,%s )''', (comment, date, pid,aid,uid,uname))
            conn.commit()
        else:
            comment = getPhotoComment(pid)
            for c in comment:
                cuid = c[4]
                newcontribution = getUserContribution(cuid) - 1
                cursor.execute("UPDATE Users SET contribution='{1}'  WHERE uid = '{0}'".format(cuid, newcontribution))
            newcontribution = getUserContribution(uid) - 1
            cursor.execute("UPDATE Users SET contribution='{1}'  WHERE uid = '{0}'".format(uid, newcontribution))
            cursor.execute("UPDATE Tags_Associates SET pid='-1'  WHERE pid = '{0}'".format(pid))
            cursor.execute("DELETE FROM Photos WHERE pid='{0}'".format(pid))
            conn.commit()
        photos = getAlbumPhotos(aid)
        photolist=[]
        for photo in photos:
            pid=photo[1]
            if pid == -1:
                continue
            numlikes=getNumLikes(pid)
            tags = getPhotoTag(pid)
            photolist.append([photo, numlikes, tags])
        return render_template('onealbum.html', uid=uid, owneruid=owneruid[0], name=getAlbumName(aid), aid=aid, comments=getAlbumComments(aid),photos=photolist,base64=base64)
    else:
        if flask_login.current_user.is_authenticated == False:
            uid = getUserIdFromEmail("anonymous@bu.edu")
        else:
            uid = getUserIdFromEmail(flask_login.current_user.id)
        aid=request.args.get('aid')
        owneruid = getAlbumOwner(aid)
        photos = getAlbumPhotos(aid)
        photolist = []
        for photo in photos:
            pid=photo[1]
            if pid == -1:
                continue
            numlikes = getNumLikes(pid)
            tags = getPhotoTag(pid)
            photolist.append([photo, numlikes, tags])
        return render_template('onealbum.html', uid=uid, owneruid=owneruid[0], name=getAlbumName(aid), aid=aid, comments=getAlbumComments(aid),photos=photolist,base64=base64)

@app.route("/like", methods=['GET','POST'])
@flask_login.login_required
def like():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    distinction = request.form.get('distinction')
    description = request.form.get('description')
    aid = request.form.get('aid')
    pid = request.form.get('pid')
    uname = getUsersName(uid)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Liked_By WHERE uid ='{0}' AND pid = '{1}'".format(uid, pid))
    count = cursor.rowcount
    if count == 0:
        message = True
        cursor.execute('''INSERT INTO  Liked_By (pid,uid,uname) VALUES (%s, %s, %s)''', (pid, uid,uname))
        conn.commit()
    else:
        message = False

    numlikes = getNumLikes(pid)
    cursor.execute("SELECT uname FROM Liked_By WHERE pid = '{0}'".format(pid))
    likedusers = cursor.fetchall()

    return render_template('like.html', message=message, aid=aid, albumname=getAlbumName(aid),likedusers=likedusers, numlikes=numlikes,
                          photo=getPhoto(pid), base64=base64, distinction=distinction,description=description)

@app.route('/mytag', methods=['GET','POST'])
@flask_login.login_required
def mytag():
    if request.method=='GET':
        description = request.args.get('description')
        photolist = []
        photos = getPhotoByTag(description)
        uid = getUserIdFromEmail(flask_login.current_user.id)
        for photo in photos:
            pid = photo[1]
            if pid == -1:
                continue
            owneruid = photo[2]
            if owneruid ==uid:
                ownername = getUsersName(owneruid)
                photodata = getPhoto(pid)
                numlikes = getNumLikes(pid)
                comment = getPhotoComment(pid)
                aid = getAlbumId(pid)
                tags = getPhotoTag(pid)
                photolist.append([photodata, numlikes, comment, tags, ownername, aid])
        return render_template('/mytag.html', description=description, uid=uid, photos=photolist, base64=base64)
    else:
        uid = getUserIdFromEmail(flask_login.current_user.id)
        cursor=conn.cursor()
        pid = request.form.get('pid')
        comment = getPhotoComment(pid)
        for c in comment:
            cuid = c[4]
            newcontribution = getUserContribution(cuid) - 1
            cursor.execute("UPDATE Users SET contribution='{1}'  WHERE uid = '{0}'".format(cuid, newcontribution))
        newcontribution = getUserContribution(uid) - 1
        cursor.execute("UPDATE Users SET contribution='{1}'  WHERE uid = '{0}'".format(uid, newcontribution))
        conn.commit()
        cursor.execute("UPDATE Tags_Associates SET pid='-1'  WHERE pid = '{0}'".format(pid))
        cursor.execute("DELETE FROM Photos WHERE pid='{0}'".format(pid))
        conn.commit()
        description = request.args.get('description')
        photolist = []
        photos = getPhotoByTag(description)
        newcontribution = getUserContribution(uid) - 1
        cursor.execute("UPDATE Users SET contribution='{1}'  WHERE uid = '{0}'".format(uid, newcontribution))
        for photo in photos:
            pid = photo[1]
            if pid == -1:
                continue
            owneruid = photo[2]
            if owneruid == uid:
                ownername = getUsersName(owneruid)
                photodata = getPhoto(pid)
                numlikes = getNumLikes(pid)
                comment = getPhotoComment(pid)
                aid = getAlbumId(pid)
                tags = getPhotoTag(pid)
                photolist.append([photodata, numlikes, comment, tags, ownername, aid])
        return render_template('/mytag.html', description=description, uid=uid, photos=photolist, base64=base64)


@app.route("/onetag", methods=['GET','POST'])
#@flask_login.login_required
def onetag():
    if request.method =='GET':
        description = request.args.get('description')
        photolist = []
        photos=getPhotoByTag(description)
        if flask_login.current_user.is_authenticated == False:
            uid = getUserIdFromEmail("anonymous@bu.edu")
        else:
            uid = getUserIdFromEmail(flask_login.current_user.id)
        for photo in photos:
            pid=photo[1]
            if pid == -1:
                continue
            owneruid=photo[2]
            ownername=getUsersName(owneruid)
            photodata=getPhoto(pid)

            numlikes=getNumLikes(pid)
            comment=getPhotoComment(pid)
            aid = getAlbumId(pid)
            tags=getPhotoTag(pid)
            photolist.append([photodata,numlikes,comment,tags,ownername,aid])
        return render_template('/onetag.html', description=description,uid=uid, photos=photolist ,base64=base64)
    else:
        if flask_login.current_user.is_authenticated == False:
            uid = getUserIdFromEmail("anonymous@bu.edu")
        else:
            uid = getUserIdFromEmail(flask_login.current_user.id)
        cursor = conn.cursor()
        comment = request.form.get('comment')
        date = datetime.today().strftime('%Y-%m-%d,%H:%M:%S')
        uname = getUsersName(uid)
        pid = request.form.get('pid')
        aid=getAlbumId(pid)
        cursor.execute(
            '''INSERT INTO  Comments_Leaves_Has (comment,date, pid, aid,uid,uname) VALUES (%s, %s,%s,%s, %s,%s )''',
            (comment, date, pid, aid, uid, uname))
        newcontribution = getUserContribution(uid) + 1
        cursor.execute("UPDATE Users SET contribution='{1}'  WHERE uid = '{0}'".format(uid, newcontribution))
        conn.commit()
        description = request.args.get('description')
        photolist = []
        photos = getPhotoByTag(description)
        for photo in photos:
            pid = photo[1]
            if pid == -1:
                continue
            owneruid = photo[2]
            ownername = getUsersName(owneruid)
            photodata = getPhoto(pid)
            numlikes = getNumLikes(pid)
            comment = getPhotoComment(pid)
            tags = getPhotoTag(pid)
            photolist.append([photodata, numlikes, comment, tags, ownername, aid])
        return render_template('/onetag.html',description=description, uid=uid, photos=photolist, base64=base64)

@app.route("/browse", methods=['GET','POST'])
#@flask_login.login_required
def browse():
    if request.method=='GET':
        photos = getAllPhotos()
        if flask_login.current_user.is_authenticated == False:
            uid = getUserIdFromEmail("anonymous@bu.edu")
        else:
            uid = getUserIdFromEmail(flask_login.current_user.id)
        taglist = getAllTags()
        return render_template('browse.html',uid=uid, users= photos,base64=base64,taglist=taglist)
    else:
        cursor = conn.cursor()
        aid = request.form.get('aid')
        owneruid = getAlbumOwner(aid)
        if flask_login.current_user.is_authenticated == False:
            uid = getUserIdFromEmail("anonymous@bu.edu")
        else:
            uid = getUserIdFromEmail(flask_login.current_user.id)
        comment = request.form.get('comment')
        date = datetime.today().strftime('%Y-%m-%d,%H:%M:%S')
        uname = getUsersName(uid)
        pid=request.form.get('pid')
        cursor.execute(
            '''INSERT INTO  Comments_Leaves_Has (comment,date, pid, aid,uid,uname) VALUES (%s, %s,%s,%s, %s,%s )''',
            (comment, date, pid, aid, uid, uname))
        newcontribution = getUserContribution(uid) + 1
        cursor.execute("UPDATE Users SET contribution='{1}'  WHERE uid = '{0}'".format(uid,newcontribution))
        conn.commit()
        photos = getAllPhotos()
        return render_template('browse.html', uid=uid, users=photos, base64=base64)

@app.route("/search", methods=['GET','POST'])
#@flask_login.login_required
def search():
    if flask_login.current_user.is_authenticated == False:
        uid = getUserIdFromEmail("anonymous@bu.edu")
    else:
        uid = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    if request.method=='GET':
        return render_template('search.html', uid=uid)
    else:
        distinction = request.form.get('distinction')
        contents = request.form.get('content')
        result=[]
        if distinction =='0':
            temp=contents.split(' ')
            content=[x.lower() for x in temp]
            photos=getPhotoByTag(content[0])
            for photo in photos:
                pid=photo[1]
                if pid == -1:
                    continue
                tags=[]
                taglist=getPhotoTag(pid)
                for tag in taglist:
                    tags.append(tag[0])
                if all(elem in tags for elem in content):
                    owneruid = photo[2]
                    ownername = getUsersName(owneruid)
                    photodata = getPhoto(pid)
                    numlikes = getNumLikes(pid)
                    comment = getPhotoComment(pid)
                    tags = getPhotoTag(pid)
                    aid=getAlbumId(pid)
                    result.append([photodata, numlikes, comment, tags, ownername, aid])
            return render_template('search.html', uid=uid, distinction=distinction, photos=result, base64=base64,content=content)
        else:
            cursor.execute("SELECT uid, count(cid) as count FROM Comments_Leaves_Has WHERE comment = '{0}' GROUP BY uid ORDER BY count DESC".format(contents))
            commenters = cursor.fetchall()
            for commenter in commenters:
                uname = getUsersName(commenter[0])
                result.append([uname,commenter[1]])
            return render_template('search.html', uid=uid, distinction=distinction, commenters=result)

@app.route("/youmaylike", methods=['GET','POST'])
@flask_login.login_required
def recommendPhoto():
    if request.method=='GET':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        likedphotos = getLikedPhotos(uid)
        taglist = getTopMyTags(uid)
        #tag=( description,count(pid) )
        result={}
        for tag in taglist:
            description = tag[0]
            photos = getPhotoByTag(description)
            #photo=description, pid, uid
            for photo in photos:
                if uid == photo[2]:
                    continue
                pid = photo[1]
                if pid in likedphotos:
                    continue
                if pid not in result:
                    result[pid]=1
                else:
                    result[pid] += 1
        result = sorted(result.items(), key=lambda item: item[1], reverse=True)
        #result={ (pid,count) }
        #list = [ [ ( (pid,count), numtags); ((pid,count),numtags) ] [] [] [] []]
        list1=[]
        list2=[]
        list3=[]
        list4=[]
        list5=[]
        for photo in result:
            numtags=len(getPhotoTag(photo[0]))
            if photo[1]==1:
                list1.append((photo,numtags))
            if photo[1]==2:
                list2.append((photo,numtags))
            if photo[1] == 3:
                list3.append((photo,numtags))
            if photo[1] == 4:
                list4.append((photo,numtags))
            if photo[1] == 5:
                list5.append((photo,numtags))
        searchlist=[]
        if list5:
            sorted(list5,key=lambda x:x[1])
            for ele in list5:
                searchlist.append(ele[0][0])
        if list4:
            sorted(list4, key=lambda x: x[1])
            for ele in list4:
                searchlist.append(ele[0][0])
        if list3:
            sorted(list3,key=lambda x:x[1])
            for ele in list3:
                searchlist.append(ele[0][0])
        if list2:
            sorted(list2,key=lambda x:x[1])
            for ele in list2:
                searchlist.append(ele[0][0])
        if list1:
            sorted(list1,key=lambda x:x[1])
            for ele in list1:
                searchlist.append(ele[0][0])

        photolist=[]
        for photo in searchlist:
            pid = photo
            if pid == -1:
                continue
            owneruid = getPhotoOwner(pid)
            ownername = getUsersName(owneruid)
            photodata = getPhoto(pid)
            numlikes = getNumLikes(pid)
            comment = getPhotoComment(pid)
            tags = getPhotoTag(pid)
            aid=getAlbumId(pid)
            photolist.append([photodata, numlikes, comment, tags, ownername, aid])
        return render_template('youmaylike.html', uid=uid, photos=photolist, base64=base64)
    else:
        uid = getUserIdFromEmail(flask_login.current_user.id)
        likedphotos = getLikedPhotos(uid)
        cursor = conn.cursor()
        comment = request.form.get('comment')
        date = datetime.today().strftime('%Y-%m-%d,%H:%M:%S')
        uname = getUsersName(uid)
        pid = request.form.get('pid')
        aid = getAlbumId(pid)
        cursor.execute(
            '''INSERT INTO  Comments_Leaves_Has (comment,date, pid, aid,uid,uname) VALUES (%s, %s,%s,%s, %s,%s )''',
            (comment, date, pid, aid, uid, uname))
        newcontribution = getUserContribution(uid) + 1
        cursor.execute("UPDATE Users SET contribution='{1}'  WHERE uid = '{0}'".format(uid, newcontribution))
        conn.commit()
        taglist = getTopMyTags(uid)
        # tag=( description,count(pid) )
        result = {}
        for tag in taglist:
            description = tag[0]
            photos = getPhotoByTag(description)
            # photo=description, pid, uid
            for photo in photos:
                if uid == photo[2]:
                    continue
                pid = photo[1]
                if pid in likedphotos:
                    continue
                if pid not in result:
                    result[pid] = 1
                else:
                    result[pid] += 1
        result = sorted(result.items(), key=lambda item: item[1], reverse=True)
        # result={ (pid,count) }
        # list = [ [ ( (pid,count), numtags); ((pid,count),numtags) ] [] [] [] []]
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        list5 = []
        for photo in result:
            numtags = len(getPhotoTag(photo[0]))
            if photo[1] == 1:
                list1.append((photo, numtags))
            if photo[1] == 2:
                list2.append((photo, numtags))
            if photo[1] == 3:
                list3.append((photo, numtags))
            if photo[1] == 4:
                list4.append((photo, numtags))
            if photo[1] == 5:
                list5.append((photo, numtags))
        searchlist = []
        if list5:
            sorted(list5, key=lambda x: x[1])
            for ele in list5:
                searchlist.append(ele[0][0])
        if list4:
            sorted(list4, key=lambda x: x[1])
            for ele in list4:
                searchlist.append(ele[0][0])
        if list3:
            sorted(list3, key=lambda x: x[1])
            for ele in list3:
                searchlist.append(ele[0][0])
        if list2:
            sorted(list2, key=lambda x: x[1])
            for ele in list2:
                searchlist.append(ele[0][0])
        if list1:
            sorted(list1, key=lambda x: x[1])
            for ele in list1:
                searchlist.append(ele[0][0])

        photolist = []
        for photo in searchlist:
            pid = photo
            if pid == -1:
                continue
            owneruid = getPhotoOwner(pid)
            ownername = getUsersName(owneruid)
            photodata = getPhoto(pid)
            numlikes = getNumLikes(pid)
            comment = getPhotoComment(pid)
            tags = getPhotoTag(pid)
            aid = getAlbumId(pid)
            photolist.append([photodata, numlikes, comment, tags, ownername, aid])
        return render_template('youmaylike.html', uid=uid, photos=photolist, base64=base64)



#default page
@app.route("/", methods=['GET'])
def hello():
    userlist = getTopUsers()
    return render_template('hello.html', message='Welecome to Photoshare',userlist=userlist)


if __name__ == "__main__":
    #this is invoked when in the shell  you run
    #$ python app.py
    app.run(port=5000, debug=True)


