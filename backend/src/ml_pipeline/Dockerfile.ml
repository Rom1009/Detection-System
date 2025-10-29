FROM python:3.13.9-slim

WORKDIR /src

RUN apt-get update && apt-get -y install rclone

COPY backend/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY .dvc ./.dvc

COPY .git ./.git

COPY *.dvc .

COPY dvc.lock dvc.lock

COPY dvc.yaml dvc.yaml

COPY params.yaml params.yaml

COPY backend/src/ml_pipeline ./ml_pipeline