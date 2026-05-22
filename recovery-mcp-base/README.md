# recovery-mcp Base Image

Base toolchain image for `recovery-mcp` — the heavy-compute recovery MCP server
(password/hash cracking, steganography cracking, disk forensics, file carving,
and memory forensics). It contains the expensive recovery software stack so the
application repository can add only its local Python package, tests, docs, and
entrypoint.

Published image:

```bash
ghcr.io/bja2142/recovery-mcp-base:latest
```

The GitHub Actions workflow builds and publishes `linux/amd64` and `linux/arm64`
variants, then creates a multi-architecture manifest.

It is built on `kalilinux/kali-rolling` so that `john` ships as the Openwall
jumbo build (with the `*2john` extractors) and the `wordlists` / `seclists`
corpora are available from apt. `stegseek` is built from source so the image
works on both architectures.

This image intentionally does not include MCP application source.
