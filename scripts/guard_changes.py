"""Reject agent edits outside code, tests, and user-facing docs."""

import subprocess
import sys

ALLOWED_PREFIXES = ("lab/", "tests/", "docs/")


def changed_paths() -> list[str]:
    # --porcelain -z avoids parsing spaces or untrusted lines in filenames.
    output = subprocess.check_output(["git", "status", "--porcelain=v1", "-z"], text=False)
    records = output.split(b"\x00")
    paths: list[str] = []
    index = 0
    while index < len(records):
        rec = records[index]
        index += 1
        if not rec:
            continue
        status = rec[:2].decode("ascii", errors="replace")
        path = rec[3:].decode("utf-8", errors="surrogateescape")
        paths.append(path)
        if "R" in status or "C" in status:
            # For rename and copy records, git includes an additional path.
            if index < len(records):
                paths.append(records[index].decode("utf-8", errors="surrogateescape"))
                index += 1
    return paths


def main() -> None:
    paths = [p for p in changed_paths() if not p.startswith(".generated/")]
    invalid = [p for p in paths if not p.startswith(ALLOWED_PREFIXES)]
    if invalid:
        print("Codex modified prohibited paths: " + ", ".join(invalid), file=sys.stderr)
        raise SystemExit(1)
    if not paths:
        print("No meaningful project changes found", file=sys.stderr)
        raise SystemExit(1)
    print("Allowed changed paths:", ", ".join(paths))


if __name__ == "__main__":
    main()
