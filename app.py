from src import create_app, socketio
from src.config.config import Config

app = create_app(Config().dev_config)

if __name__ == "__main__":
    socketio.run(app, 
                 host=app.config['HOST'],
                 port=app.config['PORT'],
                 debug=app.config['DEBUG'])