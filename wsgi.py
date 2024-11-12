import eventlet
eventlet.monkey_patch()  # Monkey patch doit être appelé avant d'importer d'autres modules

from app import app 

if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 8080)), app)
