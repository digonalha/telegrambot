FROM python:3.8-slim-buster
ADD . /app
WORKDIR /app
RUN apt-get update && \
    yes | apt-get install libpq-dev gcc  && \
    python -m pip install -r requirements.txt
CMD python main.py

