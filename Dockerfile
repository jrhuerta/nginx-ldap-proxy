FROM python:3-buster

LABEL maintainer="Joaquin Rodriguez <jrhuerta@gmail.com>"

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && apt-get -yq install \
        libsasl2-dev \
        libldap2-dev

COPY install-nginx-debian.sh /

RUN bash /install-nginx-debian.sh \
    && mkdir -p /tmp/nginx/cache \
    && mkdir -p /var/www/html

COPY etc/nginx /etc/nginx

RUN chown -R nginx:nginx /var/www/html

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

## Install gunicorn and supervisor
RUN python -m pip install --upgrade pip \
    && python -m pip install gunicorn supervisor

COPY app /opt/app

WORKDIR /opt/app

RUN python -m pip install -r requirements.txt

CMD ["/usr/local/bin/supervisord", "-c", "/opt/app/supervisord.conf"]