import os
import threading
from dotenv import load_dotenv

from app import create_app, socketio
from app.services.cleanup_service import schedule_cleanup_job

# Load environment variables
load_dotenv()

# Create the Flask application instance
app = create_app()

if __name__ == "__main__":
    # Start the automatic cleanup job in the background (local dev only)
    cleanup_thread = threading.Thread(target=schedule_cleanup_job, args=(24,), daemon=True)
    cleanup_thread.start()
    
    # Run using SocketIO (local dev only)
    # Gunicorn should be used in production
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    port = int(os.getenv("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=debug)
