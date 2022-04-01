FROM python:3.8-alpine
ADD . /app
WORKDIR /app
ENV TZ="America/Sao_Paulo"
RUN apk update && \
    apk add --no-cache --virtual .build-deps musl-dev postgresql-dev build-base && \
    python3 -m pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

CMD python3 main.py