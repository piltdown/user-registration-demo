From python:3.9-slim-buster
WORKDIR /usr/src/flask-project
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . .
