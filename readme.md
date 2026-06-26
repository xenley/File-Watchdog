## File Watchdog 
A simple script to watch a folder and notify you if anything inside it changes.
I built this after reading about how tools like Tripwire work for detecting file tampering and i wanted to understand the logic behind so i made this random project for fun!

## How it works
1. You choose what folderand it hashes every file inside (SHA-256) then saves the sha hashes to a `baseline.json`.
2. Later you will run it again on the same folder that you have choosen and then it re-hashes everything and compares against the baseline.json
3. It will tells you what's been **modified**, what's **new**, and what's **missing**.

## Usage
Create a baseline:

```
python watchdog.py --init /path/to/folder
```

Check for changes later:

```
python watchdog.py --check /path/to/folder
```

## Example
```
$ python watchdog.py --init testfolder
scans test folder
baseline saved -> testfolder/baseline.json
two files saved

$ python watchdog.py --check testfolder

scan finished at time it finished.

[MODIFIED] 1 file(s):
  - config.txt

[NEW] 1 file(s):
  - newfile.txt

[MISSING] 1 file(s):
  - file1.txt
```

## Notes
- Use's Python standard library, nothing more to install.
- The baseline file (`baseline.json`) gets saved inside the folder you're checking and then if you want too reset it do re-run `--init`.
- This won't catch someone editing a file and then editing it back to look identical content wise with a matching timestamp.

