#FROM --platform=i386 i386/debian:bookworm
#cmake -B build -S .  -DWITH_QRENCODE=OFF -DBUILD_GUI=OFF -DCMAKE_CXX_FLAGS="-m32" \
FROM debian:bookworm
ARG DEBIAN_FRONTEND=noninteractive
COPY patches/custom-genesis.patch /custom-genesis.patch
COPY build-bitcoin.sh /build-bitcoin.sh
RUN apt-get clean && apt-get update && apt-get -y upgrade && \
	apt-get -y install apt-utils gcc screen tmux \
	python3 python3-pip vim unzip binutils tcpdump wget \
	fakeroot dbus base whiptail hexedit python3-venv \
	patch wamerican ucf manpages procps jq \
	file git luajit make lua5.4 dialog curl \
	less cowsay netcat-openbsd iproute2 iputils-ping\
	build-essential cmake pkgconf python3-dev libgmp3-dev \
	libevent-dev libboost-dev libsqlite3-dev libcapnp-dev capnproto  && \
	bash /build-bitcoin.sh && rm /build-bitcoin.sh /custom-genesis.patch && \
	mkdir -p /tmplibs && \
	apt-get remove -y cmake pkgconf  \
	patch git  && apt-get -y autoremove --purge && \
	apt-get clean -y && \
	find / -type f -executable | grep "bin" | while read fn; do (file $fn 2>/dev/null | grep ELF 1>/dev/null 2>/dev/null && strip $fn || true); done

RUN wget https://github.com/tsl0922/ttyd/releases/latest/download/ttyd.$(uname -m) -O /ttyd && chmod +x /ttyd

RUN useradd -m user && echo "user:password" | chpasswd
# We set WORKDIR, as this gets extracted by Webvm to be used as the cwd. This is optional.
WORKDIR /home/user/

RUN echo 'root:password' | chpasswd

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY peer-discovery.sh /usr/local/bin/peer-discovery.sh
RUN chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/peer-discovery.sh


RUN mkdir -p /home/user/scripts
COPY agent.py /home/user/scripts/agent.py
COPY miner.py /home/user/scripts/miner.py
RUN chown -R user:user /home/user/scripts 

USER user 


# Environment toggles for the lab (override with docker compose or docker run -e ...)
ENV BITCOIN_DATADIR="/home/user/.bitcoin" \
    BITCOIN_EXTRA_ARGS="" \
    SEED_HOSTS="instructor:8333" \
    AUTO_SCAN="1" \
    AUTO_WALLET="0" \
    SCAN_NET="auto"

# Use the entrypoint to start bitcoind in background, then exec your ttyd/tmux
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]


RUN python3 -m venv .venv

RUN echo "echo 'source /home/user/.venv/bin/activate' >> /home/user/.bashrc"

RUN /bin/bash -c "source /home/user/.venv/bin/activate && pip3 install bitcoinlib"

# We set env, as this gets extracted by Webvm. This is optional.
ENV HOME="/home/user" TERM="xterm" USER="user" SHELL="/bin/bash" EDITOR="vim" LANG="en_US.UTF-8" LC_ALL="C"

CMD [ "/ttyd", "-W", "/bin/tmux", "new", "-As0" ]
