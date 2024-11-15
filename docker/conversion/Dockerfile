FROM continuumio/miniconda3:24.7.1-0

RUN conda install -y \
    lxml \
    pandas \
    tifffile \
 && conda clean --all

WORKDIR /opt
COPY data /opt
COPY bin /opt

CMD ["/bin/bash"]
