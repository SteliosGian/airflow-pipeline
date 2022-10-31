FROM apache/airflow:2.2.2-python3.8

ARG PIPENV_VERSION_=2022.6.7
ENV PIP_NO_CACHE_DIR=false
ENV PIPENV_INSTALL_TIMEOUT=3000

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
            openjdk-11-jre-headless \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

RUN pip install pipenv==${PIPENV_VERSION_}

COPY Pipfile ./Pipfile
COPY Pipfile.lock ./Pipfile.lock

RUN pipenv install --system --ignore-pipfile
