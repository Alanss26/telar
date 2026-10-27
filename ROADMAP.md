# Roadmap

What comes after v0.1. The full, prioritized list of features lands with the v0.1 docs.

## Pending chores

### Move the working copy into the WSL filesystem

The repo currently lives on the Windows drive (`/mnt/c/...`) and is used from WSL2. Move it to
`~/telar` inside WSL.

- **Why:** files under `/mnt/c` are slow to read from Linux, uv can't hardlink from its cache
  (hence `UV_LINK_MODE=copy`), and edits made from Windows don't trigger inotify, so `telar dev`
  needs `--poll` to notice them.
- **Difficulty:** low. Clone or move the repo, then run `make install` again.
- **Touches:** no code. After the move, `UV_LINK_MODE=copy` can go from `~/.bashrc`. `--poll` stays,
  since it's still useful on network drives and Docker volumes.
