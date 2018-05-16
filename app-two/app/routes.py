#!/usr/bin/python
from flask import Flask, render_template, request, jsonify, flash, url_for, redirect
from app import app, diffie, db
import requests
import json
from datetime import datetime
from .models import Message
from sqlalchemy import desc
key = None
all_msg = None
msg_id = 0

@app.route('/', methods=['GET', 'POST'])
def index():
    if key == None and request.method == 'POST':
        resp = dh()
        return resp
    else:
        flash(key)
        return render_template('index.html', text='Start chating')

def dh():
    global key
    p = int(request.json['p'])
    g = int(request.json['g'])
    A = int(request.json['A'])
    b, B = diffie.start(p, g)
    data = jsonify({ 'B' : str(B) })
    k = diffie.create_key(A, b, p)
    key = k[0:32].encode('ascii', 'ignore')
    return data

@app.route('/send', methods=['GET', 'POST'])
def send():
    global key
    global all_msg
    enc = diffie.encrypt(key, request.form['text'])
    all_msg = 'all' in request.form
    enc = enc.decode('utf-8')
    requests.post('http://server-one/request',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({'msg': enc}))
    new_message = Message(text = request.form['text'], user = 'you', time = datetime.now())
    db.session.add(new_message)
    db.session.commit()
    return redirect(url_for('chat', _external=True))

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    global msg_id
    global all_msg
    if all_msg:
        rows = db.session.query(Message).all()
    else:
        rows = db.session.query(Message).filter(Message.id > msg_id).all()
    #msg_id=id last entry from bd
    row = db.session.query(Message.id).order_by(Message.id.desc()).limit(1).one()
    msg_id = row.id
    return render_template('chat.html', posts=rows)

@app.route('/request', methods=['POST'])
def response():
    global key
    enc = request.json['msg'].encode('utf-8')
    msg = diffie.decrypt(key, enc)
    new_message = Message(text = msg, user = 'not', time = datetime.now())
    db.session.add(new_message)
    db.session.commit()
    return jsonify({"status": "ok"})