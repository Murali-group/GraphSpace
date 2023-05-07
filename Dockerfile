FROM ubuntu:16.04
WORKDIR /code
# Update package lists and install necessary packages
RUN apt-get update -y && \
    apt-get install -y aptitude && \
    aptitude install -y build-essential checkinstall software-properties-common python-software-properties && \
    aptitude install -y wget git libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev && \
    aptitude install -y nodejs nodejs-legacy npm && \
    aptitude install -y postgresql postgresql-contrib && \
    aptitude install -y python2.7-dev python-pip && \
    aptitude install -y openjdk-8-jre openjdk-8-jdk && \
    aptitude install -y tcl && \
    aptitude update && \
    aptitude install -y zookeeperd

# Install Python 2.7.13 from source
RUN mkdir ~/Downloads && \
    cd ~/Downloads/ && \
    wget https://www.python.org/ftp/python/2.7.13/Python-2.7.13.tgz && \
    tar -xvf Python-2.7.13.tgz && \
    cd Python-2.7.13 && \
    ./configure && \
    make && \
    make install && \
    cd && \
    # Clean up downloaded files
    rm -rf ~/Downloads

# Install Bower
RUN npm install -g bower

# Configure git
RUN git config --global user.email "makam.subramanyam.code@gmail.com" && \
    git config --global user.name "bruce-wayne99"

# Install virtualenv
RUN wget https://bootstrap.pypa.io/pip/2.7/get-pip.py && \
    python2.7 get-pip.py && \
    pip install virtualenv

RUN pip install django

# Install Elasticsearch
RUN cd /tmp && \
    wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.5.1.tar.gz && \
    tar xvzf elasticsearch-5.5.1.tar.gz && \
    mv elasticsearch-5.5.1 /elasticsearch && \
    # Clean up downloaded files
    rm -f elasticsearch-5.5.1.tar.gz && \
    chmod -R 777 /elasticsearch

# Install Redis
RUN cd /tmp && \
    wget http://download.redis.io/redis-stable.tar.gz && \
    tar xzvf redis-stable.tar.gz && \
    cd redis-stable && \
    make && \
    make install && \
    mkdir /redis && \
    cp redis.conf /redis/ && \
    # Clean up downloaded files
    rm -f /tmp/redis-stable.tar.gz && \
    cd / && \
    chmod -R 777 /redis

# Clone GraphSpace repository
RUN cd / && \
    git clone -b comment-system https://github.com/bruce-wayne99/GraphSpace.git && \
    # Set appropriate permissions
    chmod -R 777 /GraphSpace && \
    # Clean up downloaded files
    rm -rf /var/cache/*

# Switch to the postgres user and initialize the database
USER postgres
RUN	/etc/init.d/postgresql start && \
    psql -c "CREATE DATABASE graphspace;" && \
    psql -c "ALTER USER postgres with PASSWORD 'deep21';" && \
    psql -d graphspace -c "CREATE EXTENSION pg_trgm;" && \
    psql -d graphspace -c "CREATE EXTENSION btree_gin;"

# Switch back to the root user and set environment variables
USER root
ENV JAVA_HOME /usr/lib/jvm/java-8-oracle
CMD ["python", "./graphspace/manage.py", "runserver", "0.0.0.0:8000"]
