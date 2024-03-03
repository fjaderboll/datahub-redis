FROM nginx:1.25.3

COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./tmp/web /usr/share/nginx/html/

#HEALTHCHECK --start-period=30s --timeout=3s CMD curl --fail -H "Connection: close" http://localhost:80/
