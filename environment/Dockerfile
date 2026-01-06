# Use Ubuntu 24.04 as base
FROM ubuntu:24.04

# Install build tools, Boost, OpenSSL, and CA certificates
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    libboost-system-dev \
    libboost-thread-dev \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy task files
COPY . /app

# Build the project
RUN mkdir -p build && cd build && cmake .. && make && mv https_client .. && cd .. && rm -rf build

# Default command to run HTTPS client
# CMD ["./build/https_client"]
