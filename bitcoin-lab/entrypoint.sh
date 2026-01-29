#!/usr/bin/env bash
set -euo pipefail

: "${BITCOIN_DATADIR:=/home/user/.bitcoin}"
: "${BITCOIN_EXTRA_ARGS:=}"
: "${SEED_HOSTS:=}"
: "${AUTO_WALLET:=0}"
: "${WALLET_NAME:=student}"
: "${AUTO_SCAN:=1}"
: "${SCAN_NET:=auto}"

CONF="${BITCOIN_DATADIR}/bitcoin.conf"
LOG="${BITCOIN_DATADIR}/debug.log"

mkdir -p "${BITCOIN_DATADIR}"

# First-boot config
if [[ ! -f "${CONF}" ]]; then
  cat > "${CONF}" <<EOF
server=1
listen=1
discover=1
dnsseed=0
txindex=1
fallbackfee=0.0001
# RPC exposed only inside the lab network; adjust as needed.
rpcbind=0.0.0.0
# Allow lab RFC1918 ranges; tighten for your setup.
rpcallowip=10.0.0.0/8
rpcallowip=172.16.0.0/12
rpcallowip=192.168.0.0/16
EOF

  # If you prefer hard-pinning the instructor as a rendezvous, uncomment the next line:
  # echo "addnode=instructor:8333" >> "${CONF}"
fi

# Start bitcoind in background (daemon mode)
# We pass -datadir explicitly and let users append custom flags with BITCOIN_EXTRA_ARGS.
bitcoind -datadir="${BITCOIN_DATADIR}" -daemon=1 ${BITCOIN_EXTRA_ARGS} || {
  echo "[entrypoint] Failed to start bitcoind"; exit 1;
}

# Wait for RPC to be ready
bitcoin-cli -rpcwait -datadir="${BITCOIN_DATADIR}" getblockchaininfo >/dev/null

# Auto-create a wallet on first run (optional)
if [[ "${AUTO_WALLET}" == "1" ]]; then
  if ! bitcoin-cli -datadir="${BITCOIN_DATADIR}" listwallets | grep -q "\"${WALLET_NAME}\""; then
    bitcoin-cli -datadir="${BITCOIN_DATADIR}" createwallet "${WALLET_NAME}" true false "" false true true >/dev/null
    echo "[entrypoint] Created wallet '${WALLET_NAME}' and loaded it on startup."
  fi
fi

# Seed hosts (space/comma-separated), e.g. "instructor:8333 student_1:8333"
if [[ -n "${SEED_HOSTS}" ]]; then
  IFS=', ' read -r -a hosts <<< "${SEED_HOSTS}"
  for h in "${hosts[@]}"; do
    # addnode keeps the connection open; seednode would fetch peers then disconnect. [2](https://developer.bitcoin.org/reference/rpc/addnode.html)[3](https://bitcoin.stackexchange.com/questions/83269/addnode-vs-seednode)
    bitcoin-cli -datadir="${BITCOIN_DATADIR}" addnode "${h}" add || true
  done
fi

# Optional subnet scanning in background for closed lab networks
if [[ "${AUTO_SCAN}" == "1" ]]; then
  /usr/local/bin/peer-discovery.sh "${BITCOIN_DATADIR}" "${SCAN_NET}" &
fi

# Tell students what's running
echo "echo" >> /home/user/.bashrc
echo "echo ────────────────────────────────────────────────────────────────" >> /home/user/.bashrc
echo "echo Bitcoin Core is already running in the background." >> /home/user/.bashrc
echo "echo - datadir  : ${BITCOIN_DATADIR}" >> /home/user/.bashrc
echo "echo - config   : ${CONF}" >> /home/user/.bashrc
echo "echo - logs     : tail -f ${LOG}" >> /home/user/.bashrc
if [[ "${AUTO_WALLET}" == "1" ]]; then
    echo "echo - wallet   : ${WALLET_NAME} (if AUTO_WALLET=1)" >> /home/user/.bashrc
fi
echo "echo - check    : bitcoin-cli -datadir=${BITCOIN_DATADIR} getblockchaininfo"  >> /home/user/.bashrc
echo "echo - peers    : bitcoin-cli -datadir=${BITCOIN_DATADIR} getpeerinfo \| jq '.[].addr'"  >> /home/user/.bashrc
echo "echo ────────────────────────────────────────────────────────────────"  >> /home/user/.bashrc
echo "echo "   >> /home/user/.bashrc

# Hand off to ttyd/tmux (the image’s CMD)
exec "$@"