# Sync Server Knowledge Base

This runbook keeps the server-side Hermes knowledge base aligned with the Git repository.

## Server Location

- Server: `43.139.69.15`
- User: `hermes`
- Path: `/home/hermes/workspaces/hk_open_api_agent`

## Pull Latest Knowledge Base

```bash
ssh root@43.139.69.15 'sudo -iu hermes bash -lc "cd ~/workspaces/hk_open_api_agent && git pull --ff-only"'
```

## Restart Hermes Gateway

Use this after changing Hermes configuration or when you want a clean gateway process.

```bash
ssh root@43.139.69.15 'uid=$(id -u hermes); XDG_RUNTIME_DIR=/run/user/$uid sudo -u hermes XDG_RUNTIME_DIR=/run/user/$uid systemctl --user restart hermes-gateway.service'
```

## Verify

```bash
ssh root@43.139.69.15 'sudo -iu hermes bash -lc "cd ~/workspaces/hk_open_api_agent && git status --short && hermes gateway status && hermes send --list qqbot"'
```

## Notes

- Do not copy local `.env` or `private/` to the server knowledge base.
- The repository's `.hermes.md` is automatically loaded when Hermes runs with this repository as its working directory.
