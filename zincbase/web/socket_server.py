import eventlet
from flask import Flask
from flask_socketio import SocketIO, send

def serve(args):
    eventlet.monkey_patch()
    print('Starting websocket server...')

    app = Flask(__name__, static_folder='/zincbase/web/static')
    socketio = SocketIO(app, message_queue=f"redis://{args.redis}", cors_allowed_origins='*')

    @socketio.on('message')
    def handle_message(message):
        pass

    @socketio.on('connect')
    def handle_connect():
        pass

    socketio.run(app)