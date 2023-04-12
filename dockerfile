
FROM python:3.9

WORKDIR /code

RUN apt update -y

RUN mkdir -p /var/log/sawtooth

COPY ./app /code/app
COPY ./packaging /code/packaging
COPY ./setup.py  /code/setup.py

RUN python3 setup.py clean --all \
    && python3 setup.py build \
    && python3 setup.py install \
    && cp -r ./app /usr/local/lib/python3.9/site-packages/air_anchor_tracker