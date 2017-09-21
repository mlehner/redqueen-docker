ARG BASE_IMAGE=resin/raspberrypi3-alpine:3.5
FROM $BASE_IMAGE

RUN apk add --no-cache nginx git


RUN mkdir /run/nginx
RUN ln -sf /dev/stderr /var/log/nginx/error.log
RUN ln -sf /dev/stdout /var/log/nginx/access.log

COPY redqueen.conf /etc/nginx/conf.d/default.conf
RUN git clone --depth 1 --branch release https://github.com/mlehner/redqueen-js-app.git /redqueen

EXPOSE 80

ENTRYPOINT [ "nginx", "-g", "daemon off;" ]

CMD [ "-c", "/etc/nginx/nginx.conf" ]
