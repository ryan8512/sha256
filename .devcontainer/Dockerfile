# Start from latest Ubuntu
FROM ubuntu:latest

# Prevent interactive prompts during install
ENV DEBIAN_FRONTEND=noninteractive

# Set environment variables
ENV REPO=sha256 \
    VLNV=secworks:crypto:sha256

# Install dependencies
RUN apt-get update && apt-get install -y \
    sudo \
    git \
    python3 \
    python3-pip \
    iverilog \
    make \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip (needed for cocotb/pyuvm)
RUN pip3 install --upgrade pip --break-system-packages

# Install FuseSoC, cocotb, pyuvm
RUN pip3 install fusesoc cocotb pyuvm --break-system-packages

# Create workspace directory
WORKDIR /workspace

# Clone your repo (optional - VS Code can mount instead)
# RUN git clone https://github.com/YOUR_USER/sha256.git $REPO

# Default command = open shell
CMD ["/bin/bash"]
