@echo off

(
if not exist Pytunes.py (
    for %%X in (git.exe) do (set FOUND=%%~$PATH:X)
    if defined FOUND (
        DEL "%~f0"
        git clone https://github.com/madclicker/PyTunes.git .pytunes
    ) else (
        echo "Git not installed. Install from: http://msysgit.github.io/"
        pause
        exit
    )
)
start cmd /c python Pytunes.py
exit
)
