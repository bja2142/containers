FROM debian:bookworm
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get clean && apt-get update && apt-get -y upgrade && \
	apt-get -y install apt-utils gcc screen tmux \
	python3 python3-pip vim unzip binutils tcpdump wget \
	fakeroot dbus base whiptail hexedit python3-venv \
	patch wamerican ucf manpages procps \
	file git luajit make lua5.4 dialog curl \
	less cowsay netcat-openbsd iproute2 iputils-ping\
	build-essential cmake pkgconf python3-dev libgmp3-dev \
	libevent-dev libboost-dev libsqlite3-dev libcapnp-dev capnproto  && \
	mkdir -p /bitcoin && cd /bitcoin && \
	git clone --depth 1 https://github.com/bitcoin/bitcoin.git  && \
	cd /bitcoin/bitcoin && \
	cmake -B build -S .  -DWITH_QRENCODE=OFF -DBUILD_GUI=OFF \
	CXXFLAGS="-Os -s"  \
	-DBUILD_BITCOIN_QT=OFF \
	-DENABLE_UPNP=OFF \
	-DENABLE_UTILS=ON \
	-DBUILD_BITCOIN_NODE=ON \
	-DCMAKE_EXE_LINKER_FLAGS="-s" \
	-DCMAKE_CXX_FLAGS="-Os -ffunction-sections -fdata-sections -fvisibility=hidden" \
	-DCMAKE_C_FLAGS="-Os -ffunction-sections -fdata-sections -fvisibility=hidden" && \
	cmake --build build -j $(nproc)  && \
	cmake --install build && \
	cd / && rm -r /bitcoin && \
	mkdir -p /tmplibs && \
	apt-get remove -y cmake pkgconf  \
	patch git  && apt-get -y autoremove --purge && \
	apt-get clean -y && \
	find / -type f -executable | grep "bin" | while read fn; do (file $fn 2>/dev/null | grep ELF 1>/dev/null 2>/dev/null && strip $fn || true); done

RUN wget https://github.com/tsl0922/ttyd/releases/latest/download/ttyd.$(uname -m) -O /ttyd && chmod +x /ttyd

RUN useradd -m user && echo "user:password" | chpasswd

WORKDIR /home/user/

RUN echo 'root:password' | chpasswd

USER user 

RUN python3 -m venv .venv

RUN echo "echo 'source /home/user/.venv/bin/activate' >> /home/user/.bashrc"

RUN /bin/bash -c "source /home/user/.venv/bin/activate && pip3 install bitcoinlib"

ENV HOME="/home/user" TERM="xterm" USER="user" SHELL="/bin/bash" EDITOR="vim" LANG="en_US.UTF-8" LC_ALL="C"

CMD [ "/ttyd", "-W", "/bin/tmux", "new", "-As0" ]
