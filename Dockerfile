# Use an official Python runtime as a parent image
FROM tiangolo/uwsgi-nginx-flask:python3.7

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./app /app

# Install any needed packages specified in requirements.txt
RUN pip install -U pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN apt-get install curl
RUN curl -sL https://deb.nodesource.com/setup_10.x -o nodesource_setup.sh
RUN cat nodesource_setup.sh
RUN bash nodesource_setup.sh

RUN apt install nodejs

RUN npm install 
RUN npm run build

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME current-song-lyrics