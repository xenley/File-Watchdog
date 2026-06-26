import hashlib
import json
import os
import sys
import time

BASELINE_FILE = "baseline.json"


def hash_file(path):
    # reading in chunks so big files don't kill memory
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def scan_folder(folder):
    hashes = {}
    for root, dirs, files in os.walk(folder):
        # skip the baseline file itself and hidden git stuff
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in files:
            if name == BASELINE_FILE:
                continue
            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, folder)
            try:
                hashes[rel_path] = hash_file(full_path)
            except (PermissionError, FileNotFoundError):
                # file might be locked or got deleted mid-scan, just skip it
                print(f"couldn't read {rel_path}, skipping")
    return hashes


def save_baseline(hashes, folder):
    path = os.path.join(folder, BASELINE_FILE)
    with open(path, "w") as f:
        json.dump(hashes, f, indent=2)
    print(f"baseline saved -> {path}")
    print(f"{len(hashes)} files tracked")


def load_baseline(folder):
    path = os.path.join(folder, BASELINE_FILE)
    if not os.path.exists(path):
        print("no baseline found. run with --init first")
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def compare(old, new):
    old_files = set(old.keys())
    new_files = set(new.keys())

    added = new_files - old_files
    removed = old_files - new_files
    same = old_files & new_files

    changed = []
    for f in same:
        if old[f] != new[f]:
            changed.append(f)

    return added, removed, changed


def main():
    if len(sys.argv) < 2:
        print("usage:")
        print("  python watchdog.py --init <folder>")
        print("  python watchdog.py --check <folder>")
        return

    mode = sys.argv[1]
    folder = sys.argv[2] if len(sys.argv) > 2 else "."

    if not os.path.isdir(folder):
        print(f"'{folder}' isn't a real folder, double check the path")
        return

    if mode == "--init":
        print(f"scanning {folder} ...")
        hashes = scan_folder(folder)
        save_baseline(hashes, folder)

    elif mode == "--check":
        old_hashes = load_baseline(folder)
        print(f"re-scanning {folder} ...")
        new_hashes = scan_folder(folder)

        added, removed, changed = compare(old_hashes, new_hashes)

        if not added and not removed and not changed:
            print("\nall clear - nothing changed since last baseline")
        else:
            print(f"\nscan finished at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            if changed:
                print(f"\n[MODIFIED] {len(changed)} file(s):")
                for f in changed:
                    print(f"  - {f}")
            if added:
                print(f"\n[NEW] {len(added)} file(s):")
                for f in added:
                    print(f"  - {f}")
            if removed:
                print(f"\n[MISSING] {len(removed)} file(s):")
                for f in removed:
                    print(f"  - {f}")
    else:
        print(f"don't recognise '{mode}', use --init or --check")


if __name__ == "__main__":
    main()
