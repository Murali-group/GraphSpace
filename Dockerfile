FROM ubuntu:18.04
WORKDIR /app
RUN apt-get -y update && apt-get install -y \
    npm \
    git \
    libpq-dev \
    libxml2 \
    libxslt-dev
RUN apt-get install -y python-pip && pip install --upgrade pip
COPY . /app
RUN pip install -r requirements.txt
RUN sh install.sh
EXPOSE 8000