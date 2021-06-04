# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
ARG BASE_CONTAINER=jupyter/scipy-notebook
FROM $BASE_CONTAINER

LABEL maintainer="antishipul@gmail.com"

USER root

RUN apt-get update                    \
    && apt-get install -y             \
    python3-pip python3-dev           \
    && cd /usr/local/bin              \
    && ln -s /usr/bin/python3 python  \
    && pip3 install --upgrade pip

RUN apt-get update          \
    && apt-get install -y   \
    apt-utils bash vim curl \
    git gcc libxslt-dev     \
    graphviz

VOLUME /notebooks

WORKDIR /notebooks

COPY . /notebooks

RUN pip install -r /notebooks/requirements.txt

RUN pwd && ls -la