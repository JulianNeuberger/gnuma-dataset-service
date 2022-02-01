FROM continuumio/miniconda3:latest

COPY . /gnuma-dataset-service

RUN conda env create -f environment.yml

RUN echo "source activate ai4-document-service" > ~/.bashrc
ENV PATH /opt/conda/envs/ai4-document-service/bin:$PATH

EXPOSE 5000

CMD python server.py