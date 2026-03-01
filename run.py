import os
from app import create_app, socketio

# Create the Flask application instance for Gunicorn
# This follows the application factory pattern
app = create_app()

if __name__ == "__main__":
    # Local development background tasks only
    from dotenv import load_dotenv
    load_dotenv()
    
    import threading
    from app.services.cleanup_service import schedule_cleanup_job
    cleanup_thread = threading.Thread(target=schedule_cleanup_job, args=(24,), daemon=True)
    cleanup_thread.start()
    
    print("Background services started. Use Gunicorn to run the server.")
