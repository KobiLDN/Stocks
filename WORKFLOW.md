# Workflow

## Two-clone setup

The repo lives in a plain container folder with two independent clones (not git worktrees). Worktrees use absolute-path pointer files that break when folders are moved or synced by Google Drive / OneDrive — two clones avoids this entirely.

```
G:\My Drive\coding\ai\Stocks\
├── STOCKSMain\   ← clone on `main` — safe copy, never edit directly
└── STOCKSDev\    ← clone on `dev`  ← all work happens here
```

## The 3-step workflow

1. **Edit in `STOCKSDev`** — make changes, commit, `git push origin dev`
2. **Sync `STOCKSMain`** — `git fetch origin` then `git merge --ff-only origin/dev`
3. **Go live** — from `STOCKSMain`: `git push` — **requires explicit user "go" every time**

`main` = sacred: always working, always deployable.
`dev` = disposable: break it freely.

## Safety net

If `STOCKSDev` gets trashed:

```
cd STOCKSDev
git fetch origin
git reset --hard origin/main
```

Or delete the folder and re-clone — `main` is always the source of truth.

## If `--ff-only` is refused

The price bot may have committed directly to `main` since your last sync. Fix:

```
cd STOCKSDev
git fetch origin
git rebase origin/main
git push --force-with-lease origin dev
```

Then retry step 2.

## Branch hygiene

- All feature work on `dev`
- `main` only ever receives fast-forward merges from `dev`
- Never commit directly to `main`
- Never force-push `main`
