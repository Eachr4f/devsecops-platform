FROM nginx:stable-alpine

USER root

RUN apk upgrade --no-cache

COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html style.css app.js /usr/share/nginx/html/

USER 101:101
EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD ["wget", "-q", "--spider", "http://127.0.0.1:8080/"]

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
