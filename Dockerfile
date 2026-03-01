FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_DEBUG=0

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies without cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose port 8080 (clean and standard for many cloud platforms)
EXPOSE 8080

# Run the app using gunicorn with gevent WebSocket worker
# Using 1 worker for WebSocket compatibility and binding to dynamic $PORT
CMD ["sh", "-c", "gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 -b 0.0.0.0:$PORT run:app"]
