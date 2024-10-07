from src import config, app
from flask_socketio import SocketIO

# Initialize the SocketIO instance with your Flask app
socketio = SocketIO(app)

if __name__ == "__main__":
    socketio.run(app, host=config.HOST, port=config.PORT, debug=config.DEBUG)
