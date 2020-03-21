import eventlet
from flask import Flask
from flask_socketio import SocketIO, send

app = Flask(__name__, static_url_path='/')

@app.route('/')
def index():
    return app.send_static_file('index.html')

def serve(args):
    eventlet.monkey_patch()
    print('Starting websocket server...')
    
    socketio = SocketIO(app, message_queue=f"redis://{args.redis}", cors_allowed_origins='*')
    
    @socketio.on('message')
    def handle_message(message):
        pass

    @socketio.on('connect')
    def handle_connect():
        pass

    socketio.run(app)
    return app