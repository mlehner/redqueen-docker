ARG BASE_IMAGE=balenalib/raspberrypi3-alpine:3.5
FROM $BASE_IMAGE

RUN apk add --no-cache python2 py2-pip py-mysqldb

RUN pip install xbee

RUN pip install arrow

ADD redqueen.py /

ENTRYPOINT [ "/redqueen.py" ]
