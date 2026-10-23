FROM ghcr.io/astral-sh/uv@sha256:a06fb406bda92ac2c105cd45111a206b80294215d6480fa4ce4fd931ab66d7b2 AS uv
FROM ubuntu@sha256:18b33ff3829707f31ada654a963b9ee35f2e6f0241b964bd17a22a9b330cb63d
COPY --from=uv /uv /usr/local/bin/uv
ENV DEBIAN_FRONTEND=noninteractive UV_PYTHON_DOWNLOADS=never UV_LINK_MODE=copy
# Explicit container-only dependencies; do not run the inherited host setup scripts.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates python3-dev python3-venv clang build-essential gcc-arm-none-eabi \
    liblzma-dev capnproto libcapnp-dev curl libcurl4-openssl-dev git \
    ffmpeg libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libavfilter-dev \
    libbz2-dev libeigen3-dev libffi-dev libglew-dev libgles2-mesa-dev libglfw3-dev \
    libglib2.0-0 libjpeg-dev libqt5charts5-dev libncurses-dev libssl-dev \
    libusb-1.0-0-dev libzmq3-dev libzstd-dev libsqlite3-dev libsystemd-dev \
    opencl-headers ocl-icd-libopencl1 ocl-icd-opencl-dev portaudio19-dev \
    qttools5-dev-tools libqt5svg5-dev libqt5serialbus5-dev libqt5x11extras5-dev \
    libqt5opengl5-dev qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools \
    && dpkg-query -W > /apt-package-manifest.txt && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --extra testing --extra dev \
    && uv pip freeze > /python-package-manifest.txt
ENV VIRTUAL_ENV=/opt/dependencies/.venv
ENV PATH=/opt/dependencies/.venv/bin:$PATH PYTHONPATH=/work:/work/tinygrad_repo
# AGNOS-specific header dependency absent from the generic host dependency list.
RUN apt-get update && apt-get install -y --no-install-recommends libi2c-dev \
    && dpkg-query -W > /apt-package-manifest.txt && rm -rf /var/lib/apt/lists/*
WORKDIR /work
