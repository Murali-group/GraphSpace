#Base Image to install & Run Graphspace
FROM ubuntu:18.04

#Created a app directory for graphspace
WORKDIR /app

#Installs required & dev packages to smoothly install graphspace rquirements on ubuntu and mac as well   
RUN apt-get -y update && apt-get install -y \
    npm \ 
    git \
    libpq-dev \
    libxml2 \
    libxslt-dev

#Installs npm globally
RUN npm install bower -g

#Installs Pip package and upgrades it 
RUN apt-get install -y python-pip && pip install --upgrade pip

#Copies whole graphspace project in app directory
COPY . /app

#Installs Graphspace requirements
RUN pip install -r requirements.txt

#Installs Graphspace
RUN sh install.sh

#Exposes the port 8000 to discover graphspace container
EXPOSE 8000