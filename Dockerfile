FROM python:3.8-slim
LABEL maintainer="ahunn@umich.edu"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /csdt_site
WORKDIR /csdt_site
COPY ./csdt_site /csdt_site

RUN adduser user
USER user

