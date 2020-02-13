FROM ubuntu:18.04
MAINTAINER Hinrich Winther <winther.hinrich@mh-hannover.de>

WORKDIR /issm

EXPOSE 80
COPY . /issm
COPY docker/local_settings.py app/local_settings.py
RUN mkdir -p /data

RUN apt-get update && apt-get install -y \
    apache2 \
    libapache2-mod-wsgi-py3 \
    python3-pip
RUN a2enmod wsgi
RUN a2dissite 000-default
COPY docker/apache2.conf /etc/apache2/sites-available/issm.conf
RUN a2ensite issm
RUN pip3 install -r requirements.txt

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

ENTRYPOINT printenv | grep -v LS_COLORS | awk '{print "export " $0}' >> /etc/apache2/envvars && /etc/init.d/apache2 start && tail -f /var/log/apache2/*.log
