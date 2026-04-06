# hpnc queue

Manage the night queue.

## hpnc queue add

Add a story to the night queue.

```bash
hpnc queue add stories/my-task.md
```

### What it does

1. Validates the file exists and is `.md`
2. Parses YAML frontmatter
3. Checks for duplicates (by file path)
4. Appends to `_hpnc/night-queue.yaml`
5. Shows confirmation with metadata summary

### Duplicate detection

Adding the same story twice is rejected with a warning.
