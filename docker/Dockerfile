# Everything in one image: the app (also serving the web frontend), Redis and the NanoMQ broker,
# started in order and supervised by s6-overlay, see rootfs/etc/s6-overlay/.
# Build from the repository root: docker build -f docker/Dockerfile -t datahub .

FROM redis:8.10.2 AS redis

# static files only, so build them once on the build platform instead of per target platform
FROM --platform=$BUILDPLATFORM node:22-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY web/ ./
RUN npm run build

FROM python:3.15-slim

ARG TARGETARCH
ARG NANOMQ_VERSION=0.25.6
ARG S6_OVERLAY_VERSION=3.2.3.2

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV TZ=Europe/Stockholm
ENV DEBIAN_FRONTEND=noninteractive
ENV SQLITE_PATH=/data/datahub.db
ENV WEB_PATH=/opt/datahub/web
ENV S6_BEHAVIOUR_IF_STAGE2_FAILS=2
# the services are already stopped in order by then, leave docker's stop timeout to Redis' final save
ENV S6_KILL_GRACETIME=500

RUN apt-get update && apt-get install -y --no-install-recommends curl tzdata iputils-ping sqlite3 xz-utils && rm -rf /var/lib/apt/lists/*

RUN case "$TARGETARCH" in amd64) s6arch=x86_64 ;; arm64) s6arch=aarch64 ;; *) echo "Unsupported architecture $TARGETARCH" && exit 1 ;; esac \
	&& for f in noarch $s6arch; do \
		curl -fsSL -o /tmp/s6-overlay.tar.xz https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-$f.tar.xz \
		&& tar -C / -Jxpf /tmp/s6-overlay.tar.xz && rm /tmp/s6-overlay.tar.xz; \
	done

RUN curl -fsSL -o /tmp/nanomq.deb https://github.com/nanomq/nanomq/releases/download/${NANOMQ_VERSION}/nanomq-${NANOMQ_VERSION}-linux-${TARGETARCH}.deb \
	&& dpkg-deb -x /tmp/nanomq.deb /tmp/nanomq && cp /tmp/nanomq/usr/local/bin/nanomq /usr/local/bin/ && rm -r /tmp/nanomq /tmp/nanomq.deb

# only the time series module is used
COPY --from=redis /usr/local/bin/redis-server /usr/local/bin/redis-cli /usr/local/bin/
COPY --from=redis /usr/local/lib/redis/modules/redistimeseries.so /usr/local/lib/redis/modules/

COPY app/requirements.txt /tmp
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

RUN useradd --system --user-group --home-dir /data --no-create-home --shell /usr/sbin/nologin datahub \
	&& mkdir /data && chown datahub:datahub /data

COPY docker/rootfs/ /
COPY app/src/ /opt/datahub/app/
COPY --from=web /web/dist/web/ /opt/datahub/web/

# for docker exec, e.g. maintenance.py
WORKDIR /opt/datahub/app
EXPOSE 8080 1883
HEALTHCHECK --start-period=60s --timeout=5s CMD curl -fsS -o /dev/null http://127.0.0.1:8080/api/state/health || exit 1
ENTRYPOINT ["/init"]
