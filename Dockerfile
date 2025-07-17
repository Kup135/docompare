FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Copy the entire project into the container
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Default command to run your script
CMD ["python", "main.py"]
