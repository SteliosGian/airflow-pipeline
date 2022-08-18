#!/bin/bash

export AIRFLOW_UID=501
export AIRFLOW_GID=0

docker-compose build

docker-compose up
