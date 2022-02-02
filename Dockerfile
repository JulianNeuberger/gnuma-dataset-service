FROM continuumio/miniconda3:latest

COPY . /gnuma-dataset-service

# install postgresql python connector dependencies
RUN apt-get update
RUN apt-get -y install libpq-dev gcc

RUN conda env create -f /gnuma-dataset-service/gnuma-datasetservice-environment.yaml
SHELL ["conda", "run", "-n", "ai4-document-service", "/bin/bash", "-c"]

EXPOSE 5000

WORKDIR /gnuma-dataset-service/src

ENTRYPOINT ["conda", "run", "-n", "ai4-document-service", "python3", "server.py"]