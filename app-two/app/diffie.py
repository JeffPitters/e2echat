#!/usr/bin/python
import pyprimes
import random
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random
from base64 import b64encode, b64decode

def start(p, g):
    buf = int(random.random()*10000)
    b = pyprimes.next_prime(buf)
    buf = divmod(g**b, p) 
    B = buf[1]
    return b, B

def create_key(A, b, p):
    buf = divmod(A**b, p)
    K = buf[1]
    h = SHA256.new()
    bytekey = str(K).encode()
    h.update(bytekey)
    return h.hexdigest()

def encrypt(key, msg):
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    encryptmsg = iv + cipher.encrypt(msg.encode())
    return b64encode(encryptmsg)

def decrypt(key, enc):
    enc = b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(key, AES.MODE_CFB, iv)
    decryptmsg = cipher.decrypt(enc[16:])
    return decryptmsg.decode('utf-8')