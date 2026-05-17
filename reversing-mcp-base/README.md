# reversing-mcp Base Image

Base toolchain image for `reversing-mcp`. It contains Ghidra, Java, PyGhidra,
and the static-analysis Python dependencies so application repositories can add
only their local Python package, docs, tests, and entrypoint.

Published image:

```bash
ghcr.io/bja2142/reversing-mcp-base:latest
```

The GitHub Actions workflow builds and publishes `linux/amd64` and
`linux/arm64` variants, then creates a multi-architecture manifest.

This image intentionally does not include MCP application source.
