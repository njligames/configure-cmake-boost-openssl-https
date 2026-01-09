FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libboost-system-dev \
    libssl-dev \
    ca-certificates \
    iptables \
    vim \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the task files into the container
# COPY . /app
