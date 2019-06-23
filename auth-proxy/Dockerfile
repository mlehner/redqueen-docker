ARG BASE_IMAGE=resin/raspberrypi3-alpine:3.5
FROM $BASE_IMAGE

RUN apk add --no-cache nginx gettext

RUN mkdir /run/nginx
RUN ln -sf /dev/stderr /var/log/nginx/error.log
RUN ln -sf /dev/stdout /var/log/nginx/access.log

COPY auth-proxy.conf /etc/nginx/conf.d/default.conf
COPY nginx-wrapper.sh /nginx-wrapper.sh

EXPOSE 80

ENTRYPOINT [ "/nginx-wrapper.sh" ]

CMD [ "-c", "/etc/nginx/nginx.conf" ]
