FROM python:3.8

WORKDIR /usr/src

RUN apt-get update && \
    apt-get install -y vim

RUN pip install PyYAML neo4j Flask flask-cors

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8

EXPOSE 5000

CMD ["python", "server.py"]
