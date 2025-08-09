FROM nvcr.io/nvidia/pytorch:24.10-py3

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV PATH="/root/.cargo/bin:${PATH}"

# Install system dependencies
RUN <<EOF
apt-get update
apt-get install -y --no-install-recommends \
  curl=7.81.0-1ubuntu1.20 \
  clang=1:14.0-55~exp2 \
  libibverbs-dev=39.0-1 \
  ibverbs-providers=39.0-1 \
  librdmacm-dev=39.0-1
rm -rf /var/lib/apt/lists/*

# Without this, the monarch build does not work
ln -s /usr/lib/x86_64-linux-gnu/libibverbs.so.1 /usr/lib/x86_64-linux-gnu/libibverbs.so
ln -s /usr/lib/x86_64-linux-gnu/libmlx5.so.1 /usr/lib/x86_64-linux-gnu/libmlx5.so
EOF

ADD https://github.com/meta-pytorch/monarch.git /workspace/monarch

WORKDIR /workspace/monarch
RUN <<EOF
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
pip install --no-cache-dir -r build-requirements.txt
pip install --no-cache-dir -r python/tests/requirements.txt
pip install --no-cache-dir --no-build-isolation -e .
EOF
