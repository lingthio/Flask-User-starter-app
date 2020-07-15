# Debian 10 distribution with Python 3.8.4 installed
FROM python:3.7-slim
MAINTAINER Hinrich Winther <winther.hinrich@mh-hannover.de>

RUN apt-get update
RUN apt-get install -y \
    gcc \
    nginx

# Should not be necessary?
#EXPOSE 80

WORKDIR /issm

RUN mkdir -p /data

# Don't copy the complete current directory in order to make caching work when running docker build
ADD app /issm/app
ADD migrations /issm/migrations
ADD tests /issm/tests

COPY ./*.py ./*.ini Version requirements.txt /issm/

COPY docker/local_settings.py app/local_settings.py
COPY docker/uwsgi.ini /issm/uwsgi.ini
COPY docker/nginx.conf /etc/nginx/sites-enabled/default

RUN pip install -r requirements.txt

# reduce image size
RUN apt-get --purge autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* 

ENV APP_NAME=ISSM \
	SECRET_KEY="changeme" \ 
	ADMINS="admin@issm.org" \
	EMAIL_SENDER_NAME=Anonymous \
	EMAIL_SENDER_EMAIL=no-one@anonymous.org \
	DEBUG=0 \
	DATA_PATH=/data/ \
	DATABASE_URI=sqlite:////data/issm.sqlite \
	MAIL_SERVER="" \
	MAIL_PORT=587 \
	MAIL_USE_SSL=0 \
	MAIL_USE_TLS=1 \
	MAIL_USERNAME="" \
	MAIL_PASSWORD="" \
	SENDGRID_API_KEY="" \
    VERSION=

ENTRYPOINT uwsgi --ini /issm/uwsgi.ini && \
           /etc/init.d/nginx start && \
           tail -f /var/log/nginx/* /var/log/issm.log