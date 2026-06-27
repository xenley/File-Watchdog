## File Watchdog 
A simple script to watch a folder and notify you if anything inside it changes.

I built this after reading about how tools like Tripwire work for detecting file tampering and i wanted to understand the logic behind so i made this random project for fun!

## How it works
1. You choose what folder you want then it hashes every file inside (SHA-256) then saves the sha hashes to the `baseline.json` file.
2. Later you can run it again on the same folder that you have chosen and then it re hashes everything and then compares against the baseline.json file.
3. It will tells you what's been **modified**, what's **new**, and what's **missing**.

## Usage
Create a baseline:
```
python watchdog.py --init /path/to/folder
```
You can also pick which hash algorithm to use (default is sha256):
```
python watchdog.py --init /path/to/folder --algo md5
```
Check for changes (when you want):
```
python watchdog.py --check /path/to/folder
```
Add `--quiet` if you only want it to print something when stuff actually changed:
```
python watchdog.py --check /path/to/folder --quiet
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
Modified and missing files show up in red, new files show up in yellow, and an all-clear scan shows up in green so its easier to tell whats going on at a glance.

## Notes
- Uses Python standard library, nothing more to install.
- The (`baseline.json`) gets saved inside the folder you're checking and then if you want to reset it do re run `--init`.
- This won't catch someone editing a file and then editing it back to look identical content wise with a matching timestamp.
- there's a ignore list near the top of the script so it doesn't track stuff you don't care about but add to it if you need to.
- colours might not show properly on some windows terminals depending on setup, works fine on mac/linux and most modern terminals.
