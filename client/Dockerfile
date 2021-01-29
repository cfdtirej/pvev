FROM python:latest

WORKDIR /usr/src/app

RUN apt-get update && \
    apt-get install -y vim

RUN pip install PyYAML neo4j

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8

