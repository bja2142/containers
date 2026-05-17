# pwn-mcp Base Image

Base toolchain image for `pwn-mcp`. It contains the expensive dynamic-analysis
software stack so application repositories can add only their local Python
package, tests, and entrypoint.

Published image:

```bash
ghcr.io/bja2142/pwn-mcp-base:latest
```

The GitHub Actions workflow builds and publishes `linux/amd64` and
`linux/arm64` variants, then creates a multi-architecture manifest.

This image intentionally does not include MCP application source.
