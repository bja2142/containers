FROM kalilinux/kali-rolling

ARG DEBIAN_FRONTEND=noninteractive
ARG STEGSEEK_VERSION=0.6

LABEL org.opencontainers.image.source="https://github.com/bja2142/containers" \
      org.opencontainers.image.description="Base toolchain image for recovery-mcp (cracking, steganography, disk/memory forensics, carving)" \
      org.opencontainers.image.licenses="MIT"

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Recovery toolchain: cracking, steganography, disk/memory forensics, carving,
# plus the wordlist corpora. Built on Kali so `john` ships as jumbo (with the
# *2john extractors and broad format coverage) and the `wordlists` / `seclists`
# packages are available.
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        python3 python3-pip \
        ca-certificates curl gzip git \
        ruby ruby-dev \
        build-essential cmake \
        libmcrypt-dev libmhash-dev libjpeg-dev zlib1g-dev \
        john hashcat \
        sleuthkit binwalk foremost testdisk bulk-extractor \
        yara ripgrep \
        steghide libimage-exiftool-perl \
        p7zip-full unzip \
        wordlists seclists; \
    rm -rf /var/lib/apt/lists/*

# Volatility 3 -- memory forensics (no apt package; userspace, unprivileged).
RUN pip3 install --no-cache-dir --break-system-packages volatility3

# zsteg -- PNG/BMP LSB steganography detection.
RUN gem install --no-document zsteg

# stegseek -- steghide cracker. Built from source so the image is multi-arch
# (upstream publishes only an amd64 .deb).
RUN set -eux; \
    git clone --depth=1 --branch "v${STEGSEEK_VERSION}" \
        https://github.com/RickdeJager/stegseek /tmp/stegseek; \
    cmake -S /tmp/stegseek -B /tmp/stegseek/build -DCMAKE_BUILD_TYPE=Release; \
    cmake --build /tmp/stegseek/build -j "$(nproc)"; \
    cmake --install /tmp/stegseek/build; \
    rm -rf /tmp/stegseek

# Decompress the rockyou wordlist shipped (gzipped) by the `wordlists` package.
RUN if [ -f /usr/share/wordlists/rockyou.txt.gz ]; then \
        gunzip -f /usr/share/wordlists/rockyou.txt.gz; \
    fi

# Verify the toolchain is present and importable; fail the build if anything
# is missing.
RUN set -eux; \
    for tool in john hashcat fls mmls icat fsstat binwalk foremost \
                bulk_extractor yara rg steghide stegseek zsteg vol exiftool; do \
        command -v "$tool" >/dev/null || { echo "missing tool: $tool" >&2; exit 1; }; \
    done; \
    python3 -c "import volatility3"; \
    test -f /usr/share/wordlists/rockyou.txt

# This image intentionally contains no MCP application source. The recovery-mcp
# application repository adds its Python package, tests, docs, and entrypoint
# on top of this base.
