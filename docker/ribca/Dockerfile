FROM continuumio/miniconda3:24.7.1-0

RUN conda config --add channels defaults \
 && conda install -y \
    -c pytorch \
    -c nvidia \
    pytorch=2.5.1 \
    torchvision=0.20.1 \
    torchaudio=2.5.1 \
    pytorch-cuda=11.8 \
    mkl=2023.1.0 \
 && conda install -y \
    -c conda-forge \
    timm=1.0.12 \
    gdown=5.2.0 \
    umap-learn=0.5.7 \
 && conda install -y \
    matplotlib=3.9.2 \
    seaborn=0.13.2 \
    scipy=1.14.1 \
    scikit-image=0.24.0 \
    scikit-learn \
    tifffile=2024.12.12 \
 && conda clean --all

COPY ribca/download_models.py /opt/ribca/download_models.py
WORKDIR /opt/ribca
RUN python download_models.py

COPY ribca /opt/ribca

ENV PYTHONPATH=/opt/ribca/src/multiplexed_image_annotator
