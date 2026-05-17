FROM python:3.11-slim-trixie

ARG GHIDRA_TAG=Ghidra_12.0.4_build
ARG GHIDRA_SHA256=c3b458661d69e26e203d739c0c82d143cc8a4a29d9e571f099c2cf4bda62a120

LABEL org.opencontainers.image.source="https://github.com/bja2142/containers" \
      org.opencontainers.image.description="Base toolchain image for reversing-mcp static analysis" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    JAVA_HOME=/opt/java/openjdk \
    REVERSING_MCP_GHIDRA_HOME=/opt/ghidra \
    PATH=/opt/java/openjdk/bin:/opt/ghidra/support:/opt/ghidra:${PATH}

WORKDIR /app

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        binutils \
        build-essential \
        ca-certificates \
        curl \
        file \
        openjdk-21-jdk-headless \
        libyara-dev \
        ssdeep \
        unzip \
    && mkdir -p /opt/java \
    && ln -s "$(dirname "$(dirname "$(readlink -f "$(command -v javac)")")")" /opt/java/openjdk \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    ghidra_url="$(python -c "import json, os, urllib.request; tag = os.environ['GHIDRA_TAG']; payload = json.load(urllib.request.urlopen(f'https://api.github.com/repos/NationalSecurityAgency/ghidra/releases/tags/{tag}')); assets = [item['browser_download_url'] for item in payload['assets'] if item['name'].endswith('.zip') and '_PUBLIC_' in item['name']]; print(assets[0] if assets else (_ for _ in ()).throw(SystemExit('No public Ghidra zip asset found for the configured tag.')))")"; \
    curl -fsSL "${ghidra_url}" -o /tmp/ghidra.zip; \
    echo "${GHIDRA_SHA256}  /tmp/ghidra.zip" | sha256sum -c -; \
    unzip -q /tmp/ghidra.zip -d /opt; \
    ghidra_dir="$(find /opt -maxdepth 1 -type d -name 'ghidra_*_PUBLIC*' | head -n 1)"; \
    ln -s "${ghidra_dir}" /opt/ghidra; \
    sed -i "s|^JAVA_HOME_OVERRIDE=.*|JAVA_HOME_OVERRIDE=${JAVA_HOME}|" /opt/ghidra/support/launch.properties; \
    rm -f /tmp/ghidra.zip

RUN python -m pip install --no-cache-dir --upgrade pip "setuptools<80" wheel \
    && python -m pip install --no-cache-dir --no-index -f /opt/ghidra/Ghidra/Features/PyGhidra/pypkg/dist pyghidra \
    && python -m pip install --no-cache-dir \
        "setuptools<80" \
        "angr==9.2.115" \
        "cxxfilt>=0.3.0,<1" \
        "flare-floss>=3.1.1,<4" \
        "mcp>=1.10.0,<2" \
        "macholib>=1.16.3,<2" \
        "pefile>=2024.8.26,<2025" \
        "pycparser==2.21" \
        "pyelftools>=0.31,<1" \
        "yara-python>=4.5.0,<5" \
        "pytest>=8.2.0,<9"

RUN python -c "import pkg_resources, pyghidra, angr, yara; print('reversing base imports ok')" \
    && floss --version \
    && file --version \
    && java -version
