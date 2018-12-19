FROM alpine
RUN apk update \
    && apk add py3-lxml make

ADD . /app
VOLUME ["/app", "/data"]
WORKDIR /app

ENTRYPOINT ["/app/convert.py"]
