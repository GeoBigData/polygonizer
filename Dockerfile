FROM continuumio/miniconda:latest

# create the conda environment
RUN mkdir /helper
COPY ./environment.yml /helper
RUN conda env create -f /helper/environment.yml
# add the scripts
ADD ./scripts /scripts
