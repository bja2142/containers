# --- Build a monolithic "Bitcoin Core + Mempool" container ---
FROM ghcr.io/bja2142/bitcoin-lab:latest

USER root

# --- OS deps for Mempool backend/frontend, DB & supervision ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg dirmngr git jq \
    mariadb-server mariadb-client \
    nginx \
    supervisor \
    make g++ python3 \
    npm  && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# --- Node.js LTS (v18+ is fine; Mempool requires v16+) ---
# (Debian Bookworm ships a recent Node; if you prefer NodeSource, swap in their repo)


# --- add Rust toolchain & build deps ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    clang cmake pkg-config libssl-dev \
 && rm -rf /var/lib/apt/lists/*


RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
    | sh -s -- -y --default-toolchain stable
ENV PATH="/root/.cargo/bin:/home/user/.cargo/bin:${PATH}"



# --- Get Mempool source (frontend + backend) ---
# We build from source to keep a single-container deployment.
# (Mempool's official docker/compose is multi-container; we're collapsing it.)  [1](https://github.com/mempool/mempool/blob/master/docker/README.md)
RUN git clone --depth 1 https://github.com/mempool/mempool.git /opt/mempool
WORKDIR /opt/mempool

# if it starts breaking, consider pinning to this commit: 20e4979628bca4ca5a3b74c4407a0ff8e3ad71a6





# --- Build backend ---
WORKDIR /opt/mempool/backend
RUN npm run preinstall && npm ci && npm run build


# --- Build frontend (static files) ---
WORKDIR /opt/mempool/frontend
#fix for proxy
RUN sed -i "s|document.location.port + '{network}|document.location.port + document.location.pathname.replace(new RegExp('/\$'), '') + '{network}|" src/app/services/websocket.service.ts && \
    sed -i "s|import { HttpClient|import { PlatformLocation } from '@angular/common';\nimport { HttpClient|" src/app/services/api.service.ts && \
    sed -i "s|private httpClient: HttpClient,|private httpClient: HttpClient, private platformLocation: PlatformLocation,|" src/app/services/api.service.ts && \
    sed -i "s|this.apiBasePath = '';| this.apiBasePath = this.platformLocation.getBaseHrefFromDOM().replace(new RegExp('/\$'), '');|" src/app/services/api.service.ts && \
    grep -rl "/resources/mining-pools/" src | xargs sed -i 's|/resources/mining-pools/|resources/mining-pools/|g'

RUN npm ci && npm run build -- --base-href './'

RUN git clone --depth 1 https://github.com/mempool/electrs /opt/mempool-electrs \
 && cd /opt/mempool-electrs \
 && cargo build --release
RUN ln -sf /opt/mempool-electrs/target/release/electrs /usr/local/bin/electrs



# --- Install frontend under Nginx web root ---
RUN mkdir -p /var/www/ && \
    cp -r dist/mempool /var/www/mempool

# --- Minimal Nginx site: serve frontend on :8080 and proxy /api to backend :8999 ---
RUN rm -f /etc/nginx/sites-enabled/default
COPY nginx-mempool.conf /etc/nginx/sites-enabled/mempool.conf
EXPOSE 8080

# --- Database initialization & configuration ---
COPY mariadb-init.sh /usr/local/bin/mariadb-init.sh
RUN chmod +x /usr/local/bin/mariadb-init.sh

COPY electrs-init.sh /usr/local/bin/electrs-init.sh
RUN chmod +x /usr/local/bin/electrs-init.sh

# --- Backend configuration: copy sample and patch with env at runtime ---
# We'll generate backend/mempool-config.json on first start using envs below.
COPY mempool-entrypoint.sh /usr/local/bin/mempool-entrypoint.sh
RUN chmod +x /usr/local/bin/mempool-entrypoint.sh

# --- Supervisord to manage mysqld, mempool-backend (node), nginx ---
COPY supervisord.conf /etc/supervisor/conf.d/mempool.conf

# --- Default environment (override as needed) ---
ENV BITCOIN_DATADIR="/home/user/.bitcoin" \
    MEMPOOL_NETWORK="mainnet" \
    MEMPOOL_HTTP_PORT="8999" \
    MEMPOOL_BACKEND_MODE="electrum" \
    ELECTRUM_HOST="127.0.0.1" \
    ELECTRUM_PORT="3000" \
    ELECTRUM_TLS_ENABLED="false" \
    CORE_RPC_HOST="127.0.0.1" \
    CORE_RPC_PORT="8332" \
    CORE_RPC_USERNAME="mempool" \
    CORE_RPC_PASSWORD="mempool" \
    CORE_RPC_TIMEOUT="60000" \
    DB_HOST="127.0.0.1" \
    DB_PORT="3306" \
    DB_NAME="mempool" \
    DB_USER="mempool" \
    DB_PASS="mempool" \
    STATS_ENABLED="true"

# If your base image still starts ttyd, we supersede it here.
ENTRYPOINT ["/usr/local/bin/mempool-entrypoint.sh"]
CMD ["supervisord","-n","-c","/etc/supervisor/supervisord.conf"]