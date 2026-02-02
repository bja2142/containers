# Bitcoin Lab Runtime (Custom Bitcoin Core Fork)


This Docker image provides a custom build of the bitcoin core toolchain which
has been forked to use a custom genesis block with relaxed miniing requirements for use in class environments. 

It is designed for instruction, experimentation, networking exercises, and protocol analysis without requiring students to compile Bitcoin Core or configure a Linux environment themselves.


## What’s Inside

*   Custom‑patched **Bitcoin Core** built from the commit 30.2 release (commit: 4d7d5f6b79d4c11c47e7a828d81296918fd11d4d)
*   A non‑privileged `user` environment
*   Python virtualenv with **bitcoinlib** preinstalled
*   **ttyd + tmux** for a browser‑based interactive terminal
*   Optional automatic peer discovery and startup scripts


***

## Running the Container

Expose the ttyd web terminal:

```bash
docker run -p 8080:7681 ghcr.io/bja2142/bitcoin-mempool:latest
```

Then open:

    http://localhost:8080

You’ll get an in‑browser terminal with Bitcoin Core already running in the background.

***

## Configuration (Optional)

The image supports environment variables:

```bash
-e BITCOIN_DATADIR="/home/user/.bitcoin"
-e BITCOIN_EXTRA_ARGS=""
-e SEED_HOSTS="instructor:8333"
-e AUTO_SCAN="1"
-e AUTO_WALLET="0"
-e SCAN_NET="auto"
```

Example:

```bash
docker run \
  -p 8080:7681 \
  -e SEED_HOSTS="10.0.0.5:8333" \
  ghcr.io/YOURORG/bitcoin-mempool:latest
```

***

## Default Login

Inside ttyd (the web terminal), you are automatically logged in as:

    user / password

Root access (if needed):

    root / password

## **Preinstalled Tools for Networking & Debugging**

The image includes a curated set of tools useful for protocol exercises:

*   `tcpdump`, `iproute2`, `iputils-ping`
*   `curl`, `wget`, `jq`
*   `hexedit`, `luajit`, Python tools
*   `screen`, `tmux`, `vim`
*   `nc` (OpenBSD netcat)

These allow students to inspect, log, manipulate, and experiment with raw Bitcoin network traffic.


##  **Python Virtual Environment with bitcoinlib**

At build time:

*   A Python venv is created in `/home/user/.venv`
*   `bitcoinlib` is installed
*   `.bashrc` is preconfigured to auto‑activate the venv

This lets students immediately script/inspect Bitcoin objects without setup.

## Web Server

A simple http.server on port 8000 is started from `/home/user/shared` so that
students can easily drop things like wallet addresses or other artifacts
and share them with each other over the command line.

##  **Configurable Environment for Lab Automation**

These ENV variables control startup behavior:

| Variable             | Description                                       |
| -------------------- | ------------------------------------------------- |
| `BITCOIN_DATADIR`    | Data directory for the node                       |
| `BITCOIN_EXTRA_ARGS` | Additional `bitcoind` command-line parameters     |
| `SEED_HOSTS`         | Comma‑separated peers to automatically connect to |
| `AUTO_SCAN`          | If `1`, auto‑scan for nearby peers                |
| `AUTO_WALLET`        | Create a wallet automatically for the student     |
| `SCAN_NET`           | Controls host‑based peer scanning behavior        |

These can be overridden via `docker run -e`.

***

## Entrypoint

The container launches via:

    ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

This script:

*   Starts `bitcoind` in the background
*   Runs optional peer-discovery
*   Initializes the user environment
*   Hands over control to `ttyd + tmux`

Students see a working terminal instantly upon connecting.


## 📂 File Structure Highlights

| Path                               | Purpose                                    |
| ---------------------------------- | ------------------------------------------ |
| `/usr/local/bin/entrypoint.sh`     | Starts bitcoind + terminal                 |
| `/usr/local/bin/peer-discovery.sh` | Automated peer scanning                    |
| `/custom-genesis.patch`            | Genesis block patch (applied during build) |
| `/build-bitcoin.sh`                | Full Bitcoin Core build script             |
| `/home/user/.venv`                 | Python venv with bitcoinlib                |
| `/ttyd`                            | Web terminal binary                        |



## AI Disclosure

I leaned on GPT 5.2 and Gemini 3 Pro for suggestions on where in the bitcoin core codebase to modify to build my patch and how to best integrate the fork
as a daemon in docker. 

I also trusted chat a little too much for suggestions on the actions workflow,
but utlimately had to publish as public so I could use the free arm runners. 

This README was also drafted with LLM assistance.