FROM python:3.9-slim

# Copying requirements separately prevents re-running pip install on every code change.
COPY requirements.txt ./

# Install production dependencies.
RUN pip install -r requirements.txt

# Copy local code to the container image.
COPY main.py /main.py
COPY database.py /database.py

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Secrets injected into container environment variables from host
ENV DB_CONN_STRING replace

# Run the service on container startup
CMD exec gunicorn -b 0.0.0.0:80 --access-logfile - main:app
