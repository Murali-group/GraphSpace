FROM ubuntu:18.04 AS prod
WORKDIR /app
RUN apt-get -y update && apt-get install -y npm && apt-get install -y git
RUN npm install bower -g
RUN apt-get install -y python-pip && pip install --upgrade pip
COPY . /app
RUN pip install -r requirements.txt
RUN sh install.sh
EXPOSE 8000
CMD python manage.py migrate --settings=graphspace.settings.local && python manage.py runserver 0.0.0.0:8000 --settings=graphspace.settings.local