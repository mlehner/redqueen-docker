ARG BASE_IMAGE=arm64v8/alpine:3.15
FROM $BASE_IMAGE as door-build

RUN apk add --no-cache python3 py3-pip py3-mysqlclient py3-arrow

ENV PYTHONUNBUFFERED=1

ENTRYPOINT [ "/redqueen.py" ]

FROM door-build as door-xbee
RUN pip install xbee
ADD redqueen-xbee.py /redqueen.py

FROM door-build as door-mqtt
RUN apk add --no-cache py3-paho-mqtt
ADD redqueen-mqtt.py /redqueen.py
