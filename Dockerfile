FROM python:3.9-slim

# Log to stdout
ENV PYTHON_BUFFERED=1

# Install virtualenv and create a virtual environment
RUN pip install --no-cache-dir virtualenv==20.6.0 && virtualenv /env --python=python3.9
ENV PATH /env/bin:$PATH

# Upgrade virtualenv pip
RUN /env/bin/pip install --upgrade pip

# Install pip requirements
WORKDIR /app
COPY requirements.txt .
RUN /env/bin/pip install --no-cache-dir -r requirements.txt

# Install nginx and copy configuration
RUN apt-get update && apt-get install -y --no-install-recommends nginx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY nginx-default.conf /etc/nginx/sites-available/default

# Copy app, generate static and set permissions
COPY . .
RUN /env/bin/python manage.py collectstatic --no-input --settings=forward_auth.settings.base && \
    chown -R www-data:www-data /app

# Expose and run app
EXPOSE 80
STOPSIGNAL SIGTERM
CMD ["/app/start_server.py"]