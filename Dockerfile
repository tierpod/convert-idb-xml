FROM alpine
RUN apk update \
    && apk add py3-lxml py3-requests

ADD . /app
VOLUME ["/app", "/data"]
WORKDIR /app

ENTRYPOINT ["/app/convert.py"]
