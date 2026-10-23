FROM jvepilot-july-c3-build:20261023
RUN apt-get update && apt-get install -y --no-install-recommends qtbase5-private-dev libwayland-dev \
    && dpkg-query -W > /apt-package-manifest.txt && rm -rf /var/lib/apt/lists/*
