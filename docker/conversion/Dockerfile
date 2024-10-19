FROM continuumio/miniconda3:24.7.1-0

RUN conda install -y \
    lxml \
    tifffile \
 && conda clean --all

WORKDIR /opt
COPY bin /opt

CMD ["/bin/bash"]
