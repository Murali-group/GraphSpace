FROM ubuntu:16.04

ENV HOME /root
ENV PYTHONVERSION 2.7.13

RUN apt-get install build-essential checkinstall
RUN apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev



RUN wget https://www.python.org/ftp/python/$PYTHONVERSION/Python-$PYTHONVERSION.tgz

RUN tar -xvf Python-$PYTHONVERSION.tgz
RUN cd Python-$PYTHONVERSION

RUN ./configure
RUN make install