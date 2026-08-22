FROM nginx:1.27-alpine

ENV TZ=America/Sao_Paulo

COPY index.html /usr/share/nginx/html/index.html
COPY nexus-nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080
