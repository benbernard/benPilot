# Base image receipt: sha256:65b71be037d325f8d4380676b58a1bf8a705c2b2d2932c297a1a17c06d86921e (frozen July build image)
FROM jvepilot-july-c3-build:20261023
RUN apt-get update && apt-get install -y --no-install-recommends qtbase5-private-dev libwayland-dev \
    && dpkg-query -W > /apt-package-manifest.txt && rm -rf /var/lib/apt/lists/*
