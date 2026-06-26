import hashlib
import json
import os
import sys
import time

BASELINE_FILE = "baseline.json"

# stuff we never want to track, add to this if you need to.
IGNORE_LIST = [".git", "__pycache__", ".DS_Store", "baseline.json"]

def hash_file(path, algo="sha256"):
    # reading in small bits so big files don't kill the memory.
    if algo == "sha256":
        h = hashlib.sha256()
    elif algo == "md5":
        h = hashlib.md5()
    elif algo == "sha1":
        h = hashlib.sha1()
    else:
        print(f"don't know the algo '{algo}', falling back to sha256.")
        h = hashlib.sha256()

    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def scan_folder(folder, algo="sha256"):
    hashes = {}
    for root, dirs, files in os.walk(folder):
        # skip anything in the ignore list
        dirs[:] = [d for d in dirs if d not in IGNORE_LIST]
        for name in files:
            if name in IGNORE_LIST:
                continue
            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, folder)
            try:
                hashes[rel_path] = hash_file(full_path, algo)
            except (PermissionError, FileNotFoundError):
                # file might be locked or got deleted mid scan, then it skips.
                print(f"couldn't read {rel_path}, skipping")
    return hashes


def save_baseline(hashes, folder, algo="sha256"):
    path = os.path.join(folder, BASELINE_FILE)
    data = {"algo": algo, "hashes": hashes}
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"baseline saved -> {path}")
    print(f"{len(hashes)} files tracked using {algo}")


def load_baseline(folder):
    path = os.path.join(folder, BASELINE_FILE)
    if not os.path.exists(path):
        print("no baseline found. run with --init first.")
        sys.exit(1)
    with open(path) as f:
        data = json.load(f)

    # handle old baselines that were saved before this will update.
    if "hashes" in data:
        return data["hashes"], data.get("algo", "sha256")
    else:
        return data, "sha256"


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
        print("  python watchdog.py --init <folder> [--algo sha256|md5|sha1]")
        print("  python watchdog.py --check <folder> [--quiet]")
        return

    mode = sys.argv[1]
    args = sys.argv[2:]

    # pull out flags first, whatever's left over is the folder path.
    quiet = "--quiet" in args
    if quiet:
        args.remove("--quiet")

    algo = "sha256"
    if "--algo" in args:
        idx = args.index("--algo")
        try:
            algo = args[idx + 1]
        except IndexError:
            print("--algo needs a value, e.g. --algo md5.")
            return
        args.pop(idx + 1)
        args.pop(idx)

    folder = args[0] if args else "."

    if not os.path.isdir(folder):
        print(f"'{folder}' isn't a real folder, check the path.")
        return

    if mode == "--init":
        if not quiet:
            print(f"scanning {folder} ...")
        hashes = scan_folder(folder, algo)
        save_baseline(hashes, folder, algo)

    elif mode == "--check":
        old_hashes, saved_algo = load_baseline(folder)
        if not quiet:
            print(f"re-scanning {folder} using {saved_algo} ...")
        new_hashes = scan_folder(folder, saved_algo)

        added, removed, changed = compare(old_hashes, new_hashes)

        if not added and not removed and not changed:
            if not quiet:
                print("\nall clear, nothing changed since last baseline!")
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
        print(f"don't recognise '{mode}', use --init or --check.")


if __name__ == "__main__":
    main()
