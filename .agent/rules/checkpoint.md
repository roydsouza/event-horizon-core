# Checkpoint Override Rule (Event Horizon Core)

**Trigger**: When the user says "checkpoint".

**Action**:
1. You MUST update the local `SYNC_LOG.md` file in the root directory with a detailed summary of all recent architectural decisions, benchmarking results, configuration updates, and paths not taken.
2. DO NOT attempt to access or update `umbra/SYNC_LOG.md`. This repository maintains its own local synchronization document.
3. After updating `SYNC_LOG.md`, run `git add .` and `git commit -m "checkpoint: <summary of phase>"` and `git push` in the local repository directory.
