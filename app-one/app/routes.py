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
    if key == None:
        dh()
        return render_template('index.html', text='')
    else:
        flash(key)
        return render_template('index.html', text='Start chating')

def dh():
    global key
    a, p, g, A = diffie.start()
    response = requests.post('http://server-two', 
        headers={'Content-Type': 'application/json'}, 
        data=json.dumps({"p": str(p), "g": str(g), "A": str(A)}))
    buf = json.loads(response.text)
    B = int(buf['B'])
    k = diffie.create_key(B, a, p)
    key = k[0:32].encode('ascii', 'ignore')
    return 0

@app.route('/send', methods=['GET', 'POST'])
def send():
    global key
    global all_msg
    enc = diffie.encrypt(key, request.form['text'])
    all_msg = 'all' in request.form
    enc = enc.decode('utf-8')
    requests.post('http://server-two/request',
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
    #curl -X POST -d '{"p":23, "g":5, "A":11}' -H "Content-Type: application/json" http://server-two