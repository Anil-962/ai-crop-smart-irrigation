import os
import threading
from dotenv import load_dotenv

from app import create_app, socketio
from app.services.cleanup_service import schedule_cleanup_job

load_dotenv()

app = create_app()

if __name__ == "__main__":
    # Start the automatic cleanup job in the background
    cleanup_thread = threading.Thread(target=schedule_cleanup_job, args=(24,), daemon=True)
    cleanup_thread.start()
    
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    # socketio.run provides the asynchronous web server for both HTTP and WebSockets
    socketio.run(app, host="0.0.0.0", port=5000, debug=debug)
