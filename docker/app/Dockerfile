FROM python:3.9.18-bookworm

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV TZ Europe/Stockholm
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3-pip curl tzdata iputils-ping
COPY tmp/requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt && rm /tmp/requirements.txt

RUN useradd --create-home appuser
USER appuser

COPY tmp/src /home/appuser/app

HEALTHCHECK CMD curl --fail -H "Connection: close" http://localhost:5000/state/health
WORKDIR /home/appuser/app

CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "4", "-k", "gevent", "--worker-tmp-dir", "/dev/shm", "wsgi:app"]
