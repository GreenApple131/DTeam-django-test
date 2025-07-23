FROM python:3.11-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
ENV APP /app
RUN mkdir $APP
WORKDIR $APP

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create static files directory
RUN mkdir -p /staticfiles

# Run the application directly
EXPOSE 8000
# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
