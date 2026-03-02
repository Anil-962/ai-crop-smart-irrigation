import os
from app import create_app, socketio

# Create the Flask application instance for Gunicorn
# This follows the application factory pattern
app = create_app()

if __name__ == "__main__":
    # Local development: load environment variables and start background services
    from dotenv import load_dotenv
    load_dotenv()
    
    import threading
    from app.services.cleanup_service import schedule_cleanup_job
    
    # Start the background cleanup service
    cleanup_thread = threading.Thread(target=schedule_cleanup_job, args=(24,), daemon=True)
    cleanup_thread.start()
    
    print("Background services started. Running server in development mode...")
    
    # Run the server using Socket.IO's run method for local development
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
