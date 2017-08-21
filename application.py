#coding=utf-8
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from passlib.context import CryptContext
from flask_jsglue import JSGlue
#from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from helpers import *
from cs50 import SQL
import time
import datetime
import os
import sys
import helpers

# configure application
app = Flask(__name__)
JSGlue(app)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response
        
# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# get a serect key for session
app.secret_key = '3832414122'

# configure SQLAlchemy Library to use SQLite database
Base = declarative_base()

class User(Base):
    # 表的名字:
    __tablename__ = 'users'

    # 表的结构:
    id = Column(Integer, primary_key=True, nullable=False)
    hash = Column(String, nullable=False)
    regtime = Column(DateTime, nullable=False)

class Song(Base):
    __tablename__ = 'songs'
    
    id = Column(Integer, primary_key=True, nullable=False)
    src = Column(String, nullable=False)
    srcid = Column(String, nullable=False)
    lang = Column(String, nullable=False)
    name = Column(String, nullable=False)
    trname = Column(String, nullable=False)
    note = Column(String, nullable=False)
    subuser = Column(String, nullable=False)
    datetime = Column(DateTime, nullable=False)

class Vote(Base):
    __tablename__ = 'votes'
    
    id = Column(Integer, primary_key=True, nullable=False)
    user = Column(String, nullable=False)
    datetime = Column(DateTime, nullable=False)
    am1 = Column(String)
    am2 = Column(String)
    noon1 = Column(String)
    noon2 = Column(String)
    noon3 = Column(String)
    pm1 = Column(String)
    pm2 = Column(String)
    n = Column(String)

engine = create_engine('sqlite:///project.db')
DBSession = sessionmaker(bind=engine)
db = SQL("sqlite:///project.db")

@app.route("/")
@login_required
def index():
    if sutil("canlogin") == "1":
        weeknow1 = db.execute("select * from system where id = 1")
        weeknow = weeknow1[0]["week"]
        status = statusback(weeknow1[0]["status"])
        statusorg = weeknow1[0]["status"]
        if statusorg=="submit" or statusorg=="fullopen":
            perlang = weeknow1[0]["perlang"]
            peruser = weeknow1[0]["peruser"]
            
            chn1 = countsong("1chn")
            eng2 = countsong("2eng")
            jpn3 = countsong("3jpn")
            elect4 = countsong("4elect")
            pure5 = countsong("5pure")
            other6 = countsong("6other")
            
            usersong = db.execute("select * from songs where subuser=:uid",uid=session["userid"])
            userc = int(len(usersong))
        
            indexinfo = "绝赞内测中！\n" + sutil("indexm") + "\n 当前周数：" + str(weeknow)
            return render_template("index.html",info=indexinfo,week=weeknow,status=status,a=1,chn=chn1, eng=eng2 ,jpn=jpn3,elect=elect4,pure=pure5,other=other6,peruser=peruser,perlang=perlang,user=userc)
        else:
            indexinfo = "绝赞内测中！\n" + sutil("indexm") + "\n 当前周数：" + str(weeknow)
            return render_template("index.html",info=indexinfo,week=weeknow,status=status)
    else:
        session.clear()
        return render_template("login_disabled.html",error=sutil("indexm"))
    
@app.route("/about")
def about():
    return render_template("about.html")
    
@app.route("/test")
def test():
    statustest = db.execute("select * from system where id=1")
    sn = statustest[0]["status"]
    return render_template("test.html",sn=sn)

@app.route("/reg2017", methods=["GET", "POST"])
def reg2017():
    session.clear()
    error = None
    if sutil("canlogin") == "1":
        if request.method == "POST":
            if request.form["stage"] == "getid":
                student = db.execute("select * from sfls2017 where no =:id",id=request.form["studentno"])
                if len(student) !=1:
                    return render_template("register.html",error="学号不在记录内")
                return render_template("reg20171.html",success="信息查询成功",stuno=int(student[0]["no"]),stuname=student[0]["name"])
            if request.form["stage"] == "confirm":
                if request.form["no2"] != request.form["no1"]:
                    return render_template("reg20170.html",error="学号前后不同")
                else:
                    return render_template("reg20172.html",info="学号验证完成，请输入密码",stuno=request.form["no1"])
            if request.form["stage"] == "enterpass":
                if request.form["password"] == "":
                    error = "密码未输入"
                    return render_template("reg20172.html",error=error)
                elif request.form["password2"] == "":
                    error = "密码未确认"
                    return render_template("reg20172.html",error=error)
                elif request.form["password"] != request.form["password2"]:
                    error = "密码不一致"
                    return render_template("reg20172.html",error=error)
                
                # hash passwords
                myctx = CryptContext(schemes=["sha256_crypt"])
                hashpw = myctx.hash(request.form["password"])
                
                # check if student no already exists
                dbsession = DBSession()
                check = dbsession.query(User).filter(User.id==request.form["no1"]).scalar()
                if check != None:
                    error = "用户已存在"
                    return render_template("register.html",error=error)
                
                # generate time of register
                now = datetime.datetime.now()
                
                # actually add user into db
                new_user = User(id=request.form["no1"], hash=hashpw, regtime=now)
                dbsession.add(new_user)
                dbsession.commit()
                dbsession.close()
                
                # remember the user
                session["userid"] = request.form["no1"]
                
                # redirect user to home page
                return redirect(url_for("index"))
        else:
            return render_template("reg20170.html")
    else:
        return render_template("login_disabled.html",error=sutil("indexm"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    # forget any user_id
    session.clear()
    
    # clean errors
    error = None
    if sutil("canlogin") == "1":
        # if user reached route via POST (as by submitting a form via POST)
        if request.method == "POST":
            if request.form["studentno"] == "":
                error = "学号未输入"
                return render_template("register.html",error=error)
            elif request.form["password"] == "":
                error = "密码未输入"
                return render_template("register.html",error=error)
            elif request.form["password2"] == "":
                error = "密码未确认"
                return render_template("register.html",error=error)
            elif request.form["password"] != request.form["password2"]:
                error = "密码不一致"
                return render_template("register.html",error=error)
            
            # hash passwords
            myctx = CryptContext(schemes=["sha256_crypt"])
            hashpw = myctx.hash(request.form["password"])
            
            # check if student no already exists
            dbsession = DBSession()
            check = dbsession.query(User).filter(User.id==request.form["studentno"]).scalar()
            if check != None:
                error = "用户已存在"
                return render_template("register.html",error=error)
            
            # generate time of register
            now = datetime.datetime.now()
            
            # actually add user into db
            new_user = User(id=request.form["studentno"], hash=hashpw, regtime=now)
            dbsession.add(new_user)
            dbsession.commit()
            dbsession.close()
            
            # remember the user
            session["userid"] = request.form["studentno"]
            
            # redirect user to home page
            return redirect(url_for("index"))
            
        else:
            error = None
            return render_template("register.html",error=None)
    else:
        return render_template("login_disabled.html",error=sutil("indexm"))
    """
    return redirect(url_for("reg2017"))
        
@app.route("/submit", methods=["GET", "POST"])
@login_required
def submit():
    error = None
    if sutil("cansubmit") == "1":
        if request.method == "POST":
            if request.form["srcsite"] == "":
                error = "来源网站未选择"
                return render_template("submit.html",error=error)
            elif request.form["songid"] == "":
                error = "歌曲id未输入"
                return render_template("submit.html",error=error)
            elif request.form["lang"] == "":
                error = "语种/分类未选择"
                return render_template("submit.html",error=error)
            elif request.form["name"] == "":
                error = "歌曲名未输入"
                return render_template("submit.html",error=error)
            
            
            # check if already exist
            dbsession = DBSession()
            check = dbsession.query(Song).filter(and_(Song.srcid==request.form["songid"],Song.src==request.form["srcsite"])).scalar()
            if check != None:
                error = "歌曲已存在"
                return render_template("submit.html",error=error)
            
            check2 = dbsession.query(Song).filter(Song.name==request.form["name"]).scalar()
            if check2 != None:
                error = "同名歌曲已存在"
                return render_template("submit.html",error=error)
                
            check3 = db.execute("select * from songs where lang = :lang",lang=request.form["lang"])
            perlang = db.execute("select * from system where id = 1")
            if len(check3) > perlang[0]["perlang"]:
                error = "本分类歌曲已满"
                return render_template("submit.html",error=error)
            
            check4 = db.execute("select * from songs where subuser = :subuser",subuser=session["userid"])
            peruser = db.execute("select * from system where id = 1")
            if len(check4) > perlang[0]["peruser"]:
                error = "用户歌曲上传已达上限"
                return render_template("submit.html",error=error)
            
            # add song to db
            now = datetime.datetime.now()
            new_song = Song(src=request.form["srcsite"],srcid=request.form["songid"],lang=request.form["lang"],name=request.form["name"],trname=request.form["trname"],note=request.form["note"],subuser=session["userid"],datetime=now)
            dbsession.add(new_song)
            dbsession.commit()
            dbsession.close()
            
            return render_template("index.html",error=None,success="歌曲提交成功")
        
        else:
            return render_template("submit.html",error=None)
    else:
        return render_template("index.html",error=sutil("submitm"))
    
@app.route("/data", methods=["GET", "POST"])
@login_required
def data():
    if sutil("canlogin") == "1":
        am1 = db.execute("select :d.* , songs.* from :d left join songs on :d.:d = songs.id limit 0,5",d="am1")
        am2 = db.execute("select :d.* , songs.* from :d left join songs on :d.:d = songs.id limit 0,5",d="am2")
        noon1 = db.execute("select :d.* , songs.* from :d left join songs on :d.:d = songs.id limit 0,5",d="noon1")
        noon2 = db.execute("select :d.* , songs.* from :d left join songs on :d.:d = songs.id limit 0,5",d="noon2")
        noon3 = db.execute("select :d.* , songs.* from :d left join songs on :d.:d = songs.id limit 0,5",d="noon3")
        pm1 = db.execute("select :d.* , songs.* from :d left join songs on :d.:d = songs.id limit 0,5",d="pm1")
        pm2 = db.execute("select :d.* , songs.* from :d left join songs on :d.:d = songs.id limit 0,5",d="pm2")
        n = db.execute("select :d.* , songs.* from :d left join songs on :d.:d = songs.id limit 0,5",d="n")
        
        for song in am1:
            song["lang"] = helpers.langback(song["lang"])
            rurl(song)
        
        for song in am2:
            song["lang"] = helpers.langback(song["lang"])
            rurl(song)
            
        for song in noon1:
            song["lang"] = helpers.langback(song["lang"])
            rurl(song)
            
        for song in noon2:
            song["lang"] = helpers.langback(song["lang"])
            rurl(song)
            
        for song in noon3:
            song["lang"] = helpers.langback(song["lang"])
            rurl(song)
            
        for song in pm1:
            song["lang"] = helpers.langback(song["lang"])
            rurl(song)
            
        for song in pm2:
            song["lang"] = helpers.langback(song["lang"])
            rurl(song)
            
        for song in n:
            song["lang"] = helpers.langback(song["lang"])
            rurl(song)
            
        
        vote = db.execute("select count(*) from (select distinct votes.user from votes)")
        user = db.execute("select count(*) from users")
        
        for user in user:
            user_count = user["count(*)"]
        for vote in vote:
            vote_count = vote["count(*)"]
        
        per1 = vote_count/user_count
        per = '%.2f%%' % (per1 * 100)
        
        return render_template("data.html",user_count=user_count,vote_count=vote_count,voteper=per,am1=am1,am2=am2,noon1=noon1,noon2=noon2,noon3=noon3,pm1=pm1,pm2=pm2,n=n)
    else:
        return render_template("login_disabled.html",error=sutil("indexm"))

@app.route("/vote", methods=["GET", "POST"])
@login_required
def vote():
    if sutil("canvote") == "1":
        if request.method == "POST":
            dbsession = DBSession()
            check = dbsession.query(Vote).filter(Vote.user==session["userid"]).scalar()
            if check != None:
                return render_template("index.html",error="已经投过票了",success=None)
            now = datetime.datetime.now()
            new_vote = Vote(user=session["userid"],datetime=now,am1=request.form["am1"],am2=request.form["am2"],noon1=request.form["noon1"],noon2=request.form["noon2"],noon3=request.form["noon3"],pm1=request.form["pm1"],pm2=request.form["pm2"],n=request.form["n"])
            dbsession.add(new_vote)
            dbsession.commit()
            dbsession.close()
            return render_template("index.html",error=None,success="投票成功")
        else:
            songs = db.execute("select * from songs order by songs.lang")
            for song in songs:
                song["lang"] = helpers.langback(song["lang"])
                rurl(song)
            count = len(songs)
            return render_template("vote.html",songs=songs, count=count, info="仔细思考！在此时段内你只有一次投票机会！",success="OPEN FOR JED!")
    else:
        return render_template("index.html",error=sutil("votem"))
    
@app.route("/userinfo", methods=["GET"])
@login_required
def userinfo():
    if sutil("canlogin") == "1":
        songs = db.execute("select * from songs where songs.subuser = :uid",uid=session["userid"])
        
        dbsession = DBSession()
        check = dbsession.query(Vote).filter(Vote.user==session["userid"]).scalar()
        if check == None:
            info = "无投票记录"
            return render_template("userinfo.html",info=info)
        
        else:        
            votes = db.execute("select * from votes where votes.user =:uid",uid=session["userid"])
            for vote in votes:
                am1 = db.execute("select * from songs where songs.id = :sid",sid=vote["am1"])
                am2 = db.execute("select * from songs where songs.id = :sid",sid=vote["am2"])
                noon1 = db.execute("select * from songs where songs.id = :sid",sid=vote["noon1"])
                noon2 = db.execute("select * from songs where songs.id = :sid",sid=vote["noon2"])
                noon3 = db.execute("select * from songs where songs.id = :sid",sid=vote["noon3"])
                pm1 = db.execute("select * from songs where songs.id = :sid",sid=vote["pm1"])
                pm2 = db.execute("select * from songs where songs.id = :sid",sid=vote["pm2"])
                n = db.execute("select * from songs where songs.id = :sid",sid=vote["n"])
            
            if songs != None:    
                for song in songs:
                    song["lang"] = helpers.langback(song["lang"])
                    rurl(song)
            else:
                return None
            
            if am1 != None:
                for song in am1:
                    song["lang"] = helpers.langback(song["lang"])
                    rurl(song)
            else:
                return None
            
            if am2 != None:
                for song in am2:
                    song["lang"] = helpers.langback(song["lang"])
                    rurl(song)
            else:
                return None
                
            if noon1 != None:
                for song in noon1:
                    song["lang"] = helpers.langback(song["lang"])
                    rurl(song)
            else:
                return None
                
            if noon2 != None:
                for song in noon2:
                    song["lang"] = helpers.langback(song["lang"])
                    rurl(song)
            else:
                return None
                
            if noon3 != None:    
                for song in noon3:
                    song["lang"] = helpers.langback(song["lang"])
                    rurl(song)
            else:
                return None
                
            if pm1 != None:
                for song in pm1:
                    song["lang"] = helpers.langback(song["lang"])
                    rurl(song)
            else:
                return None
                
            if pm2 != None:
                for song in pm2:
                    song["lang"] = helpers.langback(song["lang"])
                    rurl(song)
            else:
                return None
            
            if n != None:    
                for song in n:
                    song["lang"] = helpers.langback(song["lang"])
                    rurl(song)
            else:
                return None
            return render_template("userinfo.html",songs=songs, am1=am1,am2=am2,noon1=noon1,noon2=noon2,noon3=noon3,pm1=pm1,pm2=pm2,n=n)
    else:
        return render_template("login_disabled.html",error=sutil("indexm"))

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    # log user out
    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""
    error = None
    # forget any user_id
    session.clear()
    if sutil("canlogin") == "1":
        # if user reached route via POST (as by submitting a form via POST)
        if request.method == "POST":
            if request.form["studentno"] == "":
                error = "学号未输入"
                return render_template("login.html",error=error)
            elif request.form["password"] == "":
                error = "密码未输入"
                return render_template("login.html",error=error)
            
            # query database for username
            dbsession = DBSession()
            user = dbsession.query(User).filter(User.id==request.form["studentno"]).scalar()
            
            # check if exist
            if user == None:
                error = "用户不存在"
                return render_template("login.html",error=error)
            
            # check password
            elif not pwd_context.verify(request.form.get("password"), user.hash):
                error = "密码错误"
                return render_template("login.html",error=error)
                
            # set session & close db connection
            session["userid"] = user.id
            dbsession.close()
            return redirect(url_for("index"))
        
        # else if user reached route via GET (as by clicking a link or via redirect)
        else:
            error = None
            flash(u'内测临时账号：学号 2333 密码 2333','info')
            flash(u'欢迎注册自己的账号尝试正常流程','success')
            return render_template("login.html")
    else:
        return render_template("login_disabled.html",error=sutil("indexm"))

@app.route("/passset", methods=["GET", "POST"])
@login_required
def passset():
    if sutil("canlogin") == "1":
        if request.method == "POST":
            if request.form["password"] == "":
                error = "密码未输入"
                return render_template("passset.html",error=error)
            elif request.form["password2"] == "":
                error = "密码未确认"
                return render_template("passset.html",error=error)
            elif request.form["password"] != request.form["password2"]:
                error = "密码不一致"
                return render_template("passset.html",error=error)
            
            myctx = CryptContext(schemes=["sha256_crypt"])
            hashpw = myctx.hash(request.form["password"])
            
            db.execute("update users set hash=:hash where users.id = :uid",hash=hashpw,uid=session["userid"])
            
            return render_template("index.html",success="密码重设成功")
        else:
            return render_template("passset.html")
    else:
        return render_template("login_disabled.html",error=sutil("indexm"))
    
@app.route("/historydata", methods=["GET"])
@login_required
def historydata():
    data = db.execute("select * from system where id = 1")
    datalink = data[0]["datalink"]
    return render_template("historydata.html",datalink=datalink)
    
@app.route("/songchange", methods=["GET", "POST"])
@login_required
def songchange():
    if sutil("canlogin") == "1":
        if request.method == "POST":
            if request.form["stage"] == "iddone":
                # check if i submitted the song
                song = db.execute("select * from songs where songs.id=:sid",sid=request.form["sid"])
                
                if len(song) != 1:
                    return render_template("songchange0.html",error="歌曲不存在")
                
                # due to some strange dict behavior
                for song1 in song:
                    subuser = song1["subuser"]
                    src = helpers.srcback(str(song1["src"]))
                    srcid = song1["srcid"]
                    lang = helpers.langback(str(song1["lang"]))
                    name = song1["name"]
                    trname = song1["trname"]
                    note = song1["note"]
                    id = song1["id"]
                    
                
                session["scid"] = id
                
                if str(subuser) != str(session["userid"]):
                    error = "不是自己提交的歌曲"
                    return render_template("songchange0.html",error=error)
                else:
                    return render_template("songchange1.html",info="正在修改歌曲数据 STEP 2 OF 2",src=src,srcid=srcid,lang=lang,name=name,trname=trname,note=note,id=session["scid"])
                    
            elif request.form["stage"] == "infodone":
                # write into db
                now = datetime.datetime.now()
                
                db.execute("UPDATE songs SET src=:src, srcid=:srcid, name=:name, trname=:trname, note=:note, datetime=:dt where songs.id = :sid",
                src=request.form["srcsite"],
                srcid=request.form["songid"],
                name=request.form["name"],
                trname=request.form["trname"],
                note=request.form["note"],
                dt=now,
                sid=session["scid"])
                
                flash(u'歌曲修改成功', 'success')
                return redirect(url_for("userinfo"))
                
            else:
                return render_template("songchange0.html",info="正在修改歌曲数据 ????")
        else:    
            return render_template("songchange0.html",info="正在修改歌曲数据 STEP 1 OF 2")
    else:
        return render_template("login_disabled.html",error=sutil("indexm"))

@app.route("/houtai", methods=["GET", "POST"])
def houtai():
    if request.method == "POST":
        if request.form["stage"] == "idcheck":
            status = db.execute("select * from system where id=1")
            hpass = status[0]["pass"]
            statusnow = status[0]["status"]
            weeknow = status[0]["week"]
            datanow = status[0]["datalink"]
            if request.form["pass"] != str(hpass):
                return render_template("houtai0.html",error="后台密码错误")
            else:
                return render_template("houtai1.html",success="后台登陆成功",sn=statusback(statusnow),w=weeknow,d=datanow)
        if request.form["stage"] == "do": 
            cs = request.form["status1"]
            w = request.form["week1"]
            d = request.form["data1"]
            db.execute("update system set status = :cs where id='1'",cs=str(cs))
            db.execute("update system set week = :w where id = 1",w=w)
            db.execute("update system set datalink = :d where id = 1",d=d)
            if request.form["clearsong"] == "ClearSongDB":
                db.execute("delete from songs")
                flash(u'歌曲库已清空','success')
            elif request.form["clearsong"] != "" and request.form["clearsong"] != "ClearSongDB":
                flash(u'歌曲库清空指令输入错误，未修改数据库','warning')
            else:
                flash(u'歌曲库未修改','info')
            
            if request.form["clearvote"] == "ClearVoteDB":
                db.execute("delete from votes")
                flash(u'投票库已清空','success')
            elif request.form["clearvote"] != "" and request.form["clearvote"] != "ClearVoteDB":
                flash(u'投票库清空指令输入错误，未修改数据库','warning')
            else:
                flash(u'投票库未修改','info')
                
            if request.form["userid"] != "":
                user = db.execute("select * from users where id=:uid",uid=request.form["userid"])
                if len(user) != 1:
                    flash(u'用户错误，可能不存在','danger')
                else:
                    myctx = CryptContext(schemes=["sha256_crypt"])
                    hashpw = myctx.hash("sflsmusic")
                    db.execute("update users set hash=:hashpw where id=:uid",hashpw=hashpw,uid=request.form["userid"])
                    flash(u'用户密码已修改为: sflsmusic','success')
                
            return render_template("test.html",success="后台修改成功")
    else:
        return render_template("houtai0.html")
