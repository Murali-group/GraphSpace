FROM ubuntu:18.04
WORKDIR /app
RUN apt-get -y update && apt-get install -y npm && apt-get install -y git && apt-get install -y libpq-dev
RUN npm install bower -g
RUN apt-get install -y python-pip && pip install --upgrade pip
COPY . /app
RUN pip install -r requirements.txt
RUN sh install.sh
EXPOSE 8000