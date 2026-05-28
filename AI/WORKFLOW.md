# Workflow

How this repo's local clones and GitHub branches are set up, and the exact
process for shipping changes. This doubles as a **reusable prompt** — paste
the fenced block below into a fresh Claude Code session to replicate this
setup on any new repo.

---

## Why this setup

- **Two independent clones, not git worktrees.** Worktrees use absolute-path
  pointer files (`.git` link + `.git/worktrees/*/gitdir`) that break when
  folders are moved/renamed or synced by Google Drive / OneDrive, and Windows
  locks the primary `.git` while a session is open. Independent clones have
  nothing to break.
- **`main` is the safe copy + the only thing that deploys live.**
  **`dev` is a disposable workbench.** If dev is trashed, main restores it.
- **GitHub `origin` is the bridge** between the two local clones.

---

## Structure

```
<project>/                 ← plain container folder (NO .git here)
├── <project>MAIN/         ← clone on `main` — safe copy + what goes live
└── <project>DEV/          ← clone on `dev`  — the workbench, all edits here
```

For this repo:

```
Stocks/
├── STOCKSMain/   (main)
└── STOCKSDev/    (dev)
```

---

## The 3-step workflow — always this order

1. **Edit in DEV** — make changes in `<project>DEV` → commit →
   `git push origin dev`
2. **Sync to MAIN** — in `<project>MAIN`: `git fetch origin` →
   `git merge --ff-only origin/dev`
3. **Save to GitHub** — from `<project>MAIN`: `git push`
   (this is what updates the live site)

---

## Hard rules

- Never edit directly in `<project>MAIN`. It is the restore point.
- Never push to `main` / go live without the user explicitly saying **"go"**.
  Step 3 requires explicit approval **every single time**.
- `main` is sacred: always working, always deployable.
- `dev` is disposable: break it freely.

---

## Safety net — if DEV is trashed

```
cd <project>DEV
git fetch origin
git reset --hard origin/main     # or just delete the folder and re-clone
```

`main` always has a known-good copy, so nothing is ever truly lost.

---

## If `git merge --ff-only` is refused in step 2

Means `dev` and `main` diverged (e.g. the price bot or another commit landed
on `main` in between):

```
cd <project>DEV
git fetch origin
git rebase origin/main
git push --force-with-lease origin dev
# then retry step 2 in <project>MAIN
```

---

## Branch hygiene

- Keep the GitHub branch list to exactly `main` and `dev`.
- Delete stale auto-generated branches (e.g. `claude/*-xxxxx`) once their
  work is confirmed to be in `main`:
  `git push origin --delete <branch>`

---

## Reusable setup prompt (for a new repo)

```
Set up this repo with a two-clone local structure and a safe DEV→MAIN→GitHub
workflow. Follow this exactly.

STRUCTURE
Create a container folder named after the project, holding TWO INDEPENDENT
CLONES of the same GitHub repo (NOT git worktrees — worktrees break on
Google Drive / Windows due to absolute-path pointer files):

  <project>/
  ├── <project>MAIN/   ← clone on `main` — the safe copy + what deploys live
  └── <project>DEV/    ← clone on `dev`  — the workbench, where all edits happen

SETUP STEPS
1. Make the container folder. Do NOT put a .git in the container itself.
2. Clone the repo into <project>MAIN (stays on `main`).
3. Clone the repo AGAIN into <project>DEV, then `git checkout dev`
   (create `dev` from `main` if it doesn't exist: `git push -u origin dev`).
4. Confirm: both clones independent, `git status` clean, dev and main both
   point at the same commit.

THE 3-STEP WORKFLOW (always this order)
1. EDIT IN DEV: make changes in <project>DEV → commit → `git push origin dev`
2. SYNC TO MAIN: in <project>MAIN → `git fetch origin`
   → `git merge --ff-only origin/dev`
3. SAVE TO GITHUB: from <project>MAIN → `git push` (updates the live site)

HARD RULES
- Never edit directly in <project>MAIN. It is the restore point.
- Never push to `main` / go live without the user explicitly saying "go".
  Step 3 requires explicit approval every single time.
- `main` is sacred: always working, always deployable.
- `dev` is disposable: break it freely.

SAFETY NET (if DEV is trashed)
  cd <project>DEV
  git fetch origin
  git reset --hard origin/main   # or delete the folder and re-clone

IF `git merge --ff-only` IS REFUSED IN STEP 2 (dev/main diverged):
  cd <project>DEV
  git fetch origin
  git rebase origin/main
  git push --force-with-lease origin dev
  # then retry step 2 in <project>MAIN

BRANCH HYGIENE
- Keep the GitHub branch list to exactly `main` and `dev`.
- Delete stale auto-generated branches (e.g. `claude/*-xxxxx`) once their
  work is in main: `git push origin --delete <branch>`

DOCUMENT IT
Add a "Repo structure & workflow" section to AGENTS.md and a
"Local development" section to README.md describing the above.
```
