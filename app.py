# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 16:56:29 2025

@author: Acer
"""

import mysql.connector as mysql
import random
import secrets
from os import getenv
from datetime import timedelta
from hashlib import sha256
from flask import Flask, redirect, url_for, session, request, render_template
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = b'K2+r%&>e.v?O5@8q;W'
app.permanent_session_lifetime = timedelta(minutes=10)
alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def connect():
    database = mysql.connect(
        host = getenv("MYSQL_HOST"),
        user = getenv("MYSQL_USER"),
        password = getenv("MYSQL_PASSWORD"),
        port = int(getenv("MYSQL_PORT")),
        database = getenv("MYSQL_DB")
    )
    return database, database.cursor()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/404/")
def notFound():
    return "<h1>404: This URL doesn't go anywhere!</h1>"

@app.route("/<code>/")
def redirectCode(code):
    found, URL = retrieveCode(code)
    if not found:
        return redirect(url_for("notFound"))
    return redirect(URL)

def retrieveCode(code):
    connection, urlCursor = connect()
    query = "SELECT urlRedirect FROM urls WHERE urlCode = %s"
    urlCursor.execute(query, (code,))
    for urlRedirect in urlCursor.fetchall():
        connection.close()
        return True, urlRedirect[0]
    connection.close()
    return False, None

def genCode():
    valid = False
    code = ""
    while not valid:
        code = ""
        for i in range(7):
            code += random.choice(alphabet)
        connection, urlCursor = connect()
        query = "SELECT urlCode FROM urls WHERE urlCode = %s"
        urlCursor.execute(query, (code,))
        valid = True
        for urlCode in urlCursor.fetchall():
            valid = False
        connection.close()
    return code

def genSalt():
    return "".join(secrets.choice(alphabet) for i in range(20))

@app.route("/main-page/")
def mainPage():
    username = None
    urlList = None
    if 'username' in session:
        username = session['username']
        connection, urlCursor = connect()
        query = "SELECT urlCode, urlRedirect FROM urls WHERE userID = (SELECT userID FROM users WHERE username = %s)"
        urlCursor.execute(query, (username,))
        urlList = list(urlCursor)
        connection.close()
    
    return render_template("mainPage.html",user=username,urls=urlList)

@app.route("/insert-url/", methods = ["POST"])
def insertURL():
    username = None
    if 'username' in session:
        username = session['username']
        url = request.form.get("url")
        code = genCode()
        connection, urlCursor = connect()
        query = "INSERT INTO urls VALUES (%s, %s, (SELECT userID FROM users WHERE username = %s))"
        urlCursor.execute(query, (code, url, username))
        connection.commit()
        connection.close()
    
    return redirect(url_for("mainPage"))

@app.route("/modify-url/<code>/", methods = ["POST"])
def modifyURL(code):
    username = None
    if 'username' in session:
        username = session['username']
        url = request.form.get("newUrl")
        connection, urlCursor = connect()
        query = "UPDATE urls SET urlRedirect = %s WHERE urlCode = %s AND userID = (SELECT userID FROM users WHERE username = %s)"
        urlCursor.execute(query, (url, code, username))
        connection.commit()
        connection.close()
    
    return redirect(url_for("mainPage"))

@app.route("/delete-url/<code>/", methods = ["POST"])
def deleteURL(code):
    username = None
    if 'username' in session:
        username = session['username']
        connection, urlCursor = connect()
        query = "DELETE FROM urls WHERE urlCode = %s AND userID = (SELECT userID FROM users WHERE username = %s)"
        urlCursor.execute(query, (code, username))
        connection.commit()
        connection.close()
    
    return redirect(url_for("mainPage"))

@app.route("/sign-up/")
def signUp():
    unError = request.args.get('errorUN')
    pwError = request.args.get('errorPW')
    
    if (unError and not pwError):
        return render_template("signUp.html", errorUN = True)
    if (unError and pwError):
        return render_template("signUp.html", errorUN = True, errorPW = True)
    if (pwError and not unError):
        return render_template("signUp.html", errorPW = True)
    return render_template("signUp.html")

@app.route("/login/")
def login():
    errorr = request.args.get('error')
    didSignUp = request.args.get('signedUp')
    
    if (errorr and not didSignUp):
        return render_template("login.html", error = True)
    if (errorr and didSignUp):
        return render_template("login.html", error = True, signedIn = True)
    if (didSignUp and not errorr):
        return render_template("login.html", signedIn = True)
    return render_template("login.html")

@app.route("/sign-up-finished/", methods = ["POST"])
def finishSignUp():
    username = request.form.get("username")
    password = request.form.get("password")
    confirm = request.form.get("confirmPassword")
    unError = False
    pwError = False
    
    if (password != confirm):
        pwError = True
    
    connection, cursor = connect()
    query = "SELECT userID FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    for userID in cursor.fetchall():
        unError = True
    
    if (pwError or unError):
        connection.close()
        return redirect(url_for("signUp", errorUN = unError, errorPW = pwError))
    
    salt = genSalt()
    passwordHash = sha256((password+salt).encode("UTF-8")).hexdigest()
    query = "INSERT INTO users (username, password, salt) VALUES (%s, %s, %s)"
    cursor.execute(query, (username, passwordHash, salt))
    connection.commit()
    
    connection.close()
    return redirect(url_for("login", error = False, signedUp = True))

@app.route("/login-finished/", methods = ["POST"])
def finishLogin():
    username = request.form.get("username")
    passwordInput = request.form.get("password")
    passwordHash = b""
    storedSalt = ""
    unError = True
    
    connection, cursor = connect()
    query = "SELECT password, salt FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    for (password, salt) in cursor.fetchall():
        storedSalt = salt
        passwordHash = password
        unError = False
    if unError:
        connection.close()
        return redirect(url_for("login", error = True, signedUp = False))
    
    passwordInputHash = sha256((passwordInput+storedSalt).encode("UTF-8")).hexdigest()
    if (passwordInputHash != passwordHash):
        connection.close()
        return redirect(url_for("login", error = True, signedUp = False))
    session.permanent = True
    session['username'] = username
    return redirect(url_for("mainPage"))

if __name__ == "__main__":
    app.run()