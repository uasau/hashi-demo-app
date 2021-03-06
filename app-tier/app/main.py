from flask import Flask, jsonify, request
from gevent import monkey
monkey.patch_all(thread=False)
import requests
import os
import json
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_socketio import SocketIO, emit


app = Flask(__name__)

app.secret_key = "super secret key"
socketio = SocketIO(app)
CORS(app)

pghost = os.environ.get('POSTGRES_HOST')
pguser = os.environ.get('POSTGRES_USER')
pgpass = os.environ.get('POSTGRES_PASSWORD')
pgport = os.environ.get('POSTGRES_PORT')
pgdb = os.environ.get('POSTGRES_DATABASE')

print(pghost)
print(pguser)
print(pgpass)
print(pgport)
print(pgdb)


@app.route("/api/post", methods=["POST"])
def insert_post():
    req = request.get_json()
    _title = req['title']
    _text = req['text']
    conn = psycopg2.connect(f"host={pghost} port={pgport} dbname={pgdb} user={pguser} password={pgpass}")
    cur = conn.cursor()
    cur.execute("INSERT INTO textData (title, text) VALUES (%s, %s)", (_title, _text))
    conn.commit()
    print("Data push happening now")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    data = cur.execute('SELECT * FROM textData ORDER BY id DESC')
    test = cur.fetchall()
    print(test)
    socketio.emit('my event', test)
    return request.data

@app.route("/api/posts", methods=["GET"])
def get_posts():
    conn = psycopg2.connect(f"host={pghost} port={pgport} dbname={pgdb} user={pguser} password={pgpass}")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    data = cur.execute('SELECT * FROM textData ORDER BY id DESC')
    test = cur.fetchall()
    return jsonify(test)

@app.route("/api/health", methods=["GET"])
def get_health():
    stats = "{'status':'completed','platform':'healthy'}"
    socketio.emit('health event', stats)
    return jsonify(stats)


@socketio.on('health event')
def handle_health(stats):
    print('received')
    return jsonify(stats)

@socketio.on('my event')
def handle_event(data):
    print('received')
    return jsonify(data)

@socketio.on('connected')
def handle_connect():
    while True:
        socketio.sleep(3)
        print('connected')


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', debug=True)
