#coding='utf-8'
import csv
import sys

from flask import redirect, render_template, request, session, url_for, flash
from functools import wraps
from cs50 import SQL


def apology(top="", bottom=""):
    """Renders message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
            ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=escape(top), bottom=escape(bottom))

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("userid") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def langback(s):
        
        if s == None:
            return None
            
        else:
            for old, new in [("1chn", "中文"), ("2eng", "英文"), ("3jpn", "日文"), ("4elect", "电音"),
                ("5pure", "纯音乐"), ("6other", "其它")]:
                s = s.replace(old, new)
            return s
            
def srcback(s):
        
        if s == None:
            return None
            
        else:
            for old, new in [("netease", "网易云"), ("qq", "QQ"), ("xiami", "虾米"), ("bilibili", "Bilibili")]:
                s = s.replace(old, new)
            return s
            
def statusback(s):
        
        if s == None:
            return None
            
        else:
            for old, new in [("idle", "空闲"), ("submit", "歌曲提交"), ("vote", "投票"), ("fullopen", "全开"), ("maintain", "维护")]:
                s = s.replace(old, new)
            return s
        
def rurl(song):
    if song["src"] == "netease":
        song["urlback"] = "http://music.163.com/#/song?id=" + song["srcid"]
    
    if song["src"] == "qq":
        song["urlback"] = "https://y.qq.com/n/yqq/song/" + song["srcid"] + "_num.html#"
    
    if song["src"] == "xiami":
        song["urlback"] = "http://www.xiami.com/song/" + song["srcid"]
    
    if song["src"] == "bilibili":
        song["urlback"] = "https://www.bilibili.com/video/" + song["srcid"]
    return song
    
def cflashm(text,mtype):
    if mtype == 'error' or mytpe == 'danger':
        text = "<strong>错误：<strong>" + text
        mtype = "danger"
    
    if mtype == 'info':
        text = "<strong>信息：<strong>" + text
    
    if mtype == 'warning':
        text = "<strong>警告：<strong>" + text
    
    if mtype == 'success':
        text = "<strong>成功：<strong>" + text
    
    return text

def cflasht(text,mtype):
    if mtype == 'error' or mytpe == 'danger':
        text = "<strong>错误：<strong>" + text
        mtype = "danger"
    
    if mtype == 'info':
        text = "<strong>信息：<strong>" + text
    
    if mtype == 'warning':
        text = "<strong>警告：<strong>" + text
    
    if mtype == 'success':
        text = "<strong>成功：<strong>" + text
    
    return mtype
    
def sutil(text):
    db = SQL("sqlite:///project.db")
    status = db.execute("select * from system where id=1")
    statusnow = status[0]["status"]
    check = db.execute("select * from messages where status=:s",s=statusnow)
    return str(check[0][text])

def countsong(text):
    db = SQL("sqlite:///project.db")
    songs = db.execute("select * from songs where lang=:lang",lang=text)
    count = len(songs)
    return int(count)