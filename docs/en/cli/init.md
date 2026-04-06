# hpnc init

Initialize HPNC in the current project.

## Usage

```bash
hpnc init
```

## What it does

1. Creates `_hpnc/` directory
2. Writes `config.yaml` with project name detected from directory
3. Writes `executor-instructions.md` template
4. Writes `night-queue.yaml` (empty queue)
5. Checks Claude Code and Codex CLI connectivity
6. Detects existing BMad configuration

## Safe to re-run

Running `hpnc init` on an already initialized project:

- **Never overwrites** existing `config.yaml`
- Creates missing files only
- Always runs connectivity checks
