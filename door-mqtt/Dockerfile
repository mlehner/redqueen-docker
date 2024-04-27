ARG BASE_IMAGE=arm64v8/alpine:3.15
FROM $BASE_IMAGE

RUN apk add --no-cache python3 py3-pip py3-mysqlclient py3-paho-mqtt py3-arrow

ADD redqueen.py /

ENV PYTHONUNBUFFERED=1

ENTRYPOINT [ "/redqueen.py" ]
