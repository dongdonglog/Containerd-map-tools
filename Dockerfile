# Use a lightweight Python image as the base image
FROM python:3.8-slim-buster

# Set the working directory
WORKDIR /app

# Copy the application files to the working directory
COPY . /app

# Install the application dependencies
RUN pip install paramiko  -i https://pypi.douban.com/simple --trusted-host=pypi.douban.com
RUN pip install werkzeug  -i https://pypi.douban.com/simple --trusted-host=pypi.douban.com
RUN pip install flask  -i https://pypi.douban.com/simple --trusted-host=pypi.douban.com

# Expose port 5000 for the Flask app to listen on
EXPOSE 5000

# Set the environment variable to run Flask in production mode
ENV FLASK_ENV=production

# Set the command to run the application
CMD ["flask", "run", "--host=0.0.0.0"]