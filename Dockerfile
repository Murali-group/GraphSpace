FROM ubuntu:16.04
MAINTAINER Melvin Mathew (melvin15may@gmail.com)

RUN apt-get update -y && \
	apt-get install -y aptitude && \
	aptitude install -y build-essential checkinstall software-properties-common python-software-properties && \
	aptitude install -y wget git libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev && \
	mkdir ~/Downloads && \
	cd ~/Downloads/ && \
	wget https://www.python.org/ftp/python/2.7.13/Python-2.7.13.tgz && \
	tar -xvf Python-2.7.13.tgz && \
	cd Python-2.7.13 && \
	./configure && \
	make && \
	make install && \
	aptitude install -y nodejs nodejs-legacy npm && \
	npm install -g bower && \
	cd && \
	git config --global user.email "melvin15may@gmail.com" && \
	git config --global user.name "Melvin Mathew" && \
	aptitude update && \
	aptitude install -y postgresql postgresql-contrib && \
	aptitude install -y python2.7-dev python-pip && \
	pip install virtualenv && \
	aptitude install -y openjdk-8-jre openjdk-8-jdk && \
	echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
	add-apt-repository -y ppa:webupd8team/java && \
	aptitude update && \
	aptitude install -y oracle-java8-installer && \
	cd ~/Downloads && \
	wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.5.1.tar.gz && \
	tar xvzf elasticsearch-5.5.1.tar.gz && \
	rm -f elasticsearch-5.5.1.tar.gz && \
	mv elasticsearch-5.5.1 /elasticsearch && \
	aptitude install tcl && \
	wget http://download.redis.io/redis-stable.tar.gz && \
	tar xzvf redis-stable.tar.gz && \
	cd redis-stable && \
	make && \
	make install && \
	mkdir /redis && \
	cp redis.conf /redis/ && \
	aptitude update && \
	aptitude install -y zookeeperd && \
	cd && \
	wget "http://ftp.cixug.es/apache/kafka/0.10.2.1/kafka_2.12-0.10.2.1.tgz" -O ~/Downloads/kafka.tgz && \
	mkdir -p /kafka && cd /kafka && \
	tar -xvzf ~/Downloads/kafka.tgz --strip 1 && \
	pip install supervisor && \
	cd / && \ 
	git clone -b master https://github.com/Murali-group/GraphSpace.git && \
	aptitude install -y python-psycopg2 libpq-dev && \
	chmod -R 777 /GraphSpace && \
	rm -r /var/cache/

USER postgres

RUN	/etc/init.d/postgresql start && \
	psql -c "CREATE DATABASE test;" && \
	psql -c "ALTER USER postgres with PASSWORD '987654321';" && \
	psql -d test -c "CREATE EXTENSION pg_trgm;"

USER root

RUN useradd -ms /bin/bash elasticsearch && \
	chmod -R 777 /elasticsearch

ENV JAVA_HOME /usr/lib/jvm/java-8-oracle