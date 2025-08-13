FROM continuumio/miniconda3:24.7.1-0

RUN apt-get update \
 && apt-get -y install \
     curl \
 && rm -rf /var/cache/apt/*

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
RUN curl -L -o /opt/ribca-crosswalk.csv https://cdn.humanatlas.io/digital-objects/ctann/ribca/v1.0/assets/ribca-crosswalk.csv

CMD ["/bin/bash"]
