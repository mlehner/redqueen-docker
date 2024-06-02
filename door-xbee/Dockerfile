ARG BASE_IMAGE=arm64v8/alpine:3.15
FROM $BASE_IMAGE

RUN apk add --no-cache python3 py3-pip py3-mysqlclient py3-arrow

RUN pip install xbee

ADD redqueen.py /

ENV PYTHONUNBUFFERED=1

ENTRYPOINT [ "/redqueen.py" ]
