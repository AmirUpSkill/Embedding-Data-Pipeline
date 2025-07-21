# Start from a lightweight, official Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching
COPY requirements.txt .

# Install the Python dependencies
# --no-cache-dir keeps the image size smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# By default, if no command is specified, this container will just start an interactive python shell.
# We will override this in the docker-compose.yml file.
CMD ["python"]
