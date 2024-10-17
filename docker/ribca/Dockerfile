FROM continuumio/miniconda3:24.7.1-0

RUN conda config --add channels defaults \
 && conda install -y \
    -c pytorch \
    -c nvidia \
    pytorch \
    torchvision \
    torchaudio \
    pytorch-cuda=11.8 \
 && conda install -y \
    -c conda-forge \
    timm \
    gdown \
    umap-learn \
 && conda install -y \
    matplotlib \
    seaborn \
    scipy \
    scikit-image \
    scikit-learn \
    tifffile

COPY ribca/download_models.py /opt/ribca/download_models.py
WORKDIR /opt/ribca
RUN python download_models.py

COPY ribca /opt/ribca

ENV PYTHONPATH=/opt/ribca/src/multiplexed_image_annotator
