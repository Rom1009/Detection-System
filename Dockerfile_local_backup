FROM apache/airflow:latest-python3.11

USER root

RUN apt-get update && apt-get install -y rclone && apt-get clean

USER airflow