# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 16:56:29 2025

@author: Acer
"""

import mysql.connector as mysql
from flask import Flask, redirect, url_for

app = Flask(__name__)
urlDatabase = mysql.connect(
    host = "localhost",
    user = "urluser",
    password = "termite",
    port = 1937,
    database = "url_shortener"
)
urlCursor = urlDatabase.cursor()

@app.route("/<code>/")
def redirectCode(code):
    found, URL = retrieveCode(code)
    if not found:
        return redirect(url_for("notFound"))
    return redirect(URL)

def retrieveCode(code):
    query = "SELECT urlRedirect FROM urls WHERE urlCode = %s"
    urlCursor.execute(query, (code,))
    for urlRedirect in urlCursor.fetchall():
        return True, urlRedirect[0]
    return False, None

@app.route("/404")
def notFound():
    return "<h1>404: This URL doesn't go anywhere!</h1>"