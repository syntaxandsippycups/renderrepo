# Use Python base image
FROM python:3.11

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app files
COPY . .

# Expose port (Render looks for this)
EXPOSE 8000

# Run with gunicorn (assuming your app is in app.py)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "server:app"]
