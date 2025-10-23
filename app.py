# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 16:56:29 2025

@author: Acer
"""

import mysql.connector as mysql
from flask import Flask, redirect, url_for

app = Flask(__name__)

def connect():
    database = mysql.connect(
        host = "localhost",
        user = "urluser",
        password = "termite",
        port = 1937,
        database = "url_shortener"
    )
    return database, database.cursor()

@app.route("/404")
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