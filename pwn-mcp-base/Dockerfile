FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG TARGETARCH
ARG DYNAMORIO_BUILD=11.91.20536
ARG RR_VERSION=5.9.0

LABEL org.opencontainers.image.source="https://github.com/bja2142/containers" \
      org.opencontainers.image.description="Base toolchain image for pwn-mcp dynamic analysis" \
      org.opencontainers.image.licenses="MIT"

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/dynamorio/bin64:${PATH}"

WORKDIR /app

# Base OS, Python, QEMU, cross-compilers, debuggers, tracing, and exploit tools.
RUN set -eux; \
    seccomp_dev_package=libseccomp-dev; \
    if [ "$(dpkg --print-architecture)" = "arm64" ]; then \
        dpkg --add-architecture amd64; \
        seccomp_dev_package=libseccomp-dev:amd64; \
    fi; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        python3 python3-dev python3-pip python3-venv python3-pexpect \
        build-essential git curl wget ca-certificates unzip \
        qemu-user qemu-user-static binfmt-support \
        file binutils patchelf \
        gcc-x86-64-linux-gnu \
        gcc-aarch64-linux-gnu \
        gcc-mipsel-linux-gnu \
        gcc-riscv64-linux-gnu \
        libc6-dev-amd64-cross \
        libc6-dev-arm64-cross \
        libc6-dev-mipsel-cross \
        libc6-dev-riscv64-cross \
        "${seccomp_dev_package}" \
        gdb-multiarch gdbserver \
        strace ltrace valgrind \
        libelf-dev libdw-dev pkg-config \
        capnproto libcapnp-dev \
        ruby ruby-dev rubygems \
        cmake nasm yara radare2; \
    rm -rf /var/lib/apt/lists/*

RUN python3 --version && qemu-x86_64-static --version && gdb-multiarch --version

# GDB enhancements.
RUN wget -qO /root/.gdbinit-gef.py \
        https://raw.githubusercontent.com/hugsy/gef/main/gef.py \
    && echo 'source /root/.gdbinit-gef.py' > /root/.gdbinit-gef

RUN git clone --depth=1 https://github.com/pwndbg/pwndbg /opt/pwndbg \
    && cd /opt/pwndbg \
    && pip install --no-cache-dir --break-system-packages . \
    && echo 'source /opt/pwndbg/gdbinit.py' > /root/.gdbinit-pwndbg \
    && rm -rf /root/.cache/pip

RUN printf '#!/bin/sh\n\
FRAMEWORK="${GDBINIT_FRAMEWORK:-gef}"\n\
if [ "$FRAMEWORK" = "pwndbg" ]; then\n\
  cp /root/.gdbinit-pwndbg /root/.gdbinit\n\
else\n\
  cp /root/.gdbinit-gef /root/.gdbinit\n\
fi\n\
exec gdb-multiarch "$@"\n' > /usr/local/bin/gdb-fw \
    && chmod +x /usr/local/bin/gdb-fw

# uftrace from source; Ubuntu's packaged version is stale for this use case.
RUN git clone --depth=1 https://github.com/namhyung/uftrace /tmp/uftrace \
    && cd /tmp/uftrace \
    && ./configure \
    && make -j"$(nproc)" \
    && make install \
    && rm -rf /tmp/uftrace

RUN strace --version && valgrind --version && uftrace --version

# Frida and DynamoRIO.
RUN pip install --no-cache-dir --break-system-packages frida frida-tools \
    && rm -rf /root/.cache/pip

RUN set -eux; \
    case "${TARGETARCH:-$(dpkg --print-architecture)}" in \
        amd64) dynamorio_prefix="DynamoRIO-Linux" ;; \
        arm64) dynamorio_prefix="DynamoRIO-AArch64-Linux" ;; \
        *) echo "Unsupported TARGETARCH for DynamoRIO: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    dynamorio_url="https://github.com/DynamoRIO/dynamorio/releases/download/cronbuild-${DYNAMORIO_BUILD}/${dynamorio_prefix}-${DYNAMORIO_BUILD}.tar.gz"; \
    wget -qO /tmp/dynamorio.tar.gz "${dynamorio_url}"; \
    tar -xzf /tmp/dynamorio.tar.gz -C /opt; \
    ln -sf "/opt/${dynamorio_prefix}-${DYNAMORIO_BUILD}" /opt/dynamorio; \
    rm /tmp/dynamorio.tar.gz

RUN frida --version && drrun -version

# rr releases use uname-style architecture names.
RUN set -eux; \
    case "${TARGETARCH:-$(dpkg --print-architecture)}" in \
        amd64) rr_arch="x86_64" ;; \
        arm64) rr_arch="aarch64" ;; \
        *) echo "Unsupported TARGETARCH for rr: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    rr_url="https://github.com/rr-debugger/rr/releases/download/${RR_VERSION}/rr-${RR_VERSION}-Linux-${rr_arch}.deb"; \
    wget -qO /tmp/rr.deb "${rr_url}"; \
    dpkg -i /tmp/rr.deb || (apt-get update && apt-get install -f -y && dpkg -i /tmp/rr.deb); \
    rm -f /tmp/rr.deb; \
    rm -rf /var/lib/apt/lists/*

RUN rr --version

# Python, Ruby, and standalone exploit/RE tooling.
RUN pip install --no-cache-dir --break-system-packages --ignore-installed \
        pwntools ropper ROPgadget==7.6 z3-solver boofuzz \
        angr unicorn==2.1.4 qiling capstone keystone-engine \
        flare-capa flare-floss yara-python \
    && rm -rf /root/.cache/pip

RUN gem install one_gadget seccomp-tools --no-document \
    && rm -rf /root/.gem

RUN wget -qO /usr/local/bin/checksec \
        https://raw.githubusercontent.com/slimm609/checksec.sh/master/checksec \
    && chmod +x /usr/local/bin/checksec

RUN git clone --depth=1 https://github.com/matrix1001/glibc-all-in-one /opt/glibc-all-in-one \
    && cd /opt/glibc-all-in-one \
    && ./update_list \
    && mkdir -p libs \
    && chmod -R a+rwX /opt/glibc-all-in-one \
    && git clone --depth=1 https://github.com/niklasb/libc-database /opt/libc-database \
    && git clone --depth=1 https://github.com/mandiant/capa-rules /opt/capa-rules

RUN python3 -c "import pwn; print('pwntools:', pwn.version)" \
    && python3 -c "import angr, claripy, cle, unicorn, qiling, capstone, keystone, yara; print('ctf imports ok')" \
    && ropper --version \
    && one_gadget --version \
    && checksec --version \
    && seccomp-tools --version \
    && capa --version \
    && test -d /opt/capa-rules \
    && floss --version \
    && yara --version \
    && r2 -v >/dev/null \
    && nasm -v
