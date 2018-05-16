#!/usr/bin/python
from app import db

class Message(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.Text, index = True) #text message
    user = db.Column(db.String(3), index = True) #you or not
    time = db.Column(db.DateTime(timezone=True), index = True) #timestamp

    def __repr__(self):
        return '<Message %r>' % (self.text)