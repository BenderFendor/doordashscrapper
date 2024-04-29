GNU nano 4.8                                     dockerfile                                                
# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Update package lists
RUN apt-get update

# Install wget
RUN apt-get install -y wget

# Download and install Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run webserver.py when the container launches
CMD ["python", "doordashscraper.py"]









