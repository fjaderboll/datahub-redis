FROM python:3.15-slim

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV TZ=Europe/Stockholm
ENV DEBIAN_FRONTEND=noninteractive
ENV SQLITE_PATH=/data/datahub.db

RUN apt-get update && apt-get install -y --no-install-recommends curl tzdata iputils-ping sqlite3 && rm -rf /var/lib/apt/lists/*
COPY tmp/requirements.txt /tmp
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

RUN useradd --create-home appuser && mkdir /data && chown appuser /data
USER appuser

COPY tmp/src /home/appuser/app

#HEALTHCHECK --start-period=30s --timeout=3s CMD curl --fail -H "Connection: close" http://localhost:5000/state/health
WORKDIR /home/appuser/app

CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "4", "-k", "gevent", "--worker-tmp-dir", "/dev/shm", "wsgi:app"]
