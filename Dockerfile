FROM tiangolo/uwsgi-nginx:python3.7

RUN pip install flask

ENV NGINX_MAX_UPLOAD 0
ENV LISTEN_PORT 80
ENV UWSGI_INI /app/uwsgi.ini
ENV STATIC_INDEX 0
ENV NGINX_WORKER_PROCESSES auto

COPY ./app /app
WORKDIR /app

RUN pip install --no-cache-dir -r /app/requirements.txt

ENV PYTHONPATH=/app

RUN mv /entrypoint.sh /uwsgi-nginx-entrypoint.sh
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/start.sh"]
