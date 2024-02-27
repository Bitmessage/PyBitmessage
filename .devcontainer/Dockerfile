FROM ubuntu:latest

ARG USERNAME=user
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl \
    flake8 \
    gh \
    git \
    gnupg2 \
    jq \
    libcap-dev \
    libssl-dev \
    pylint \
    python3 \
    python3-dev \
    python3-flake8 \
    python3-pip \
    python3-pycodestyle \
    software-properties-common \
    sudo \
    zsh

RUN apt-add-repository ppa:deadsnakes/ppa

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python2.7 python2.7-dev

RUN pip install 'tox<4' 'virtualenv<20.22.0'

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && chsh -s /usr/bin/zsh user \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME
