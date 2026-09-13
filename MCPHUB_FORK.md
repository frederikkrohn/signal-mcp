# MCPHub fork policy

- `upstream` is an exact mirror of `googlarz/signal-mcp` `main`.
- `mcphub` contains only MCPHub-specific fixes and is the deployment branch.
- Automated upstream updates arrive as pull requests; resolve conflicts and test before merging.
- Submit generally useful fixes upstream and remove the local patch after an upstream release includes it.
- Do not commit instance configuration, credentials, Signal data, SQLite stores, or runtime caches.
