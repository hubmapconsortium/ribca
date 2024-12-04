FROM continuumio/miniconda3:24.7.1-0

RUN conda install -y \
    lxml \
    pandas \
    pytables \
    tifffile \
 && conda clean --all \
 && pip --no-cache-dir install hubmap-ome-utils==0.3.4

WORKDIR /opt
COPY data /opt
COPY bin /opt

CMD ["/bin/bash"]
