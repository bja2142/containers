
# Bitcoin Core + Mempool (All‑in‑One Container)

This image bundles **Bitcoin Core**, **Mempool backend**, **Mempool frontend**, **MariaDB**, **Electrs**, and **Nginx** into a **single self‑contained container**. It's designed for teaching, testing, and running local Mempool instances without needing multiple services or Docker Compose.

This container is built on top of the `bitcoin-lab` base image, which includes a custom‑patched Bitcoin Core environment.

***

## What This Container Includes

*   A custom **Bitcoin Core** 
*   **Mempool backend** (Node.js)
*   **Mempool frontend** (static build served by Nginx)
*   **MariaDB** for backend storage
*   **Electrs** compiled from source
*   **Nginx** to serve the UI and proxy API requests
*   **Supervisord** to orchestrate all services inside one container

All Mempool components run inside one container for simplicity. This should
not be run in production and should only be used in classroom environments. 

***

## How to Run It

Expose the Mempool UI:

```bash
docker run -p 8080:8080 ghcr.io/bja2142/bitcoin-core-mempool:latest
```

Then open:

    http://localhost:8080

The UI will load once the backend, database, and electrs finish initializing.

***

## Configuration

You can override defaults via environment variables:

```bash
-e MEMPOOL_NETWORK=mainnet
-e CORE_RPC_HOST=127.0.0.1
-e CORE_RPC_PORT=8332
-e CORE_RPC_USERNAME=mempool
-e CORE_RPC_PASSWORD=mempool
-e ELECTRUM_HOST=127.0.0.1
-e ELECTRUM_PORT=3000
-e DB_HOST=127.0.0.1
-e DB_USER=mempool
-e DB_PASS=mempool
```

Example:

```bash
docker run \
  -p 8080:8080 \
  -e MEMPOOL_NETWORK=testnet \
  ghcr.io/YOURORG/bitcoin-core-mempool:latest
```

***

## How It Works (Quick Overview)

1.  **mempool-entrypoint.sh**
    *   Initializes the MariaDB database
    *   Generates `mempool-config.json` based on environment variables
    *   Starts `electrs`, Mempool backend (Node.js), MariaDB, and Nginx under supervisord

2.  **Nginx**
    *   Serves the frontend on port **8080**
    *   Proxies `/api` requests to the Mempool backend on port **8999**

3.  **Electrs**
    *   Indexes blocks from Bitcoin Core inside the container
    *   Provides Electrum RPC for backend lookups

Everything is wired internally, so no external services are required.

***

## Why This Container Exists

This image collapses all of Mempool’s microservices into **one portable container**, making it ideal for:

*   Classroom labs
*   Private Bitcoin test networks
*   Research environments
*   Air‑gapped setups
*   CTF challenges

No Docker Compose. No external dependencies. One container and you’re good to go.

## AI Disclosure

I leaned on GPT 5.2 and Gemini 3 Pro for guidance on merging mempool into a single runtime. This was a background task so chat actually works pretty nicely when you can't do focused work and just copy/paste mindlessly. 

I also trusted chat a little too much for suggestions on the actions workflow,
but utlimately had to publish as public so I could use the free arm runners. 

This README was also drafted with LLM assistance.