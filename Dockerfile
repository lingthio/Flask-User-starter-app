FROM ubuntu:18.04
MAINTAINER Hinrich Winther <winther.hinrich@mh-hannover.de>

WORKDIR /issm

EXPOSE 80
RUN mkdir -p /data
COPY . /issm
COPY docker/local_settings.py app/local_settings.py
COPY docker/uwsgi.ini /issm/uwsgi.ini
COPY docker/nginx.conf /etc/nginx/sites-enabled/default

RUN apt-get update && apt-get install -y \
    nginx \
    python3-pip
RUN pip3 install -r requirements.txt
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 10

ENV APP_NAME           ISSM
ENV SECRET_KEY         "changeme"
ENV ADMINS             "admin@issm.org"
ENV EMAIL_SENDER_NAME  Anonymous
ENV EMAIL_SENDER_EMAIL no-one@anonymous.org
ENV DEBUG              0
ENV DATA_PATH          /data/
ENV DATABASE_URI       sqlite:////data/issm.sqlite
ENV MAIL_SERVER        ""
ENV MAIL_PORT          587
ENV MAIL_USE_SSL       0
ENV MAIL_USE_TLS       1
ENV MAIL_USERNAME      ""
ENV MAIL_PASSWORD      ""
ENV SENDGRID_API_KEY   ""

ENTRYPOINT uwsgi --ini /issm/uwsgi.ini && \
           /etc/init.d/nginx start && \
           tail -f /var/log/nginx/* /var/log/issm.log