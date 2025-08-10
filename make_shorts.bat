@echo off
setlocal enabledelayedexpansion

REM -------- CONFIG --------
set MUSIC=PYTI - I Wanna Dance [NCS Release].mp3
set FLAGS=--music-start 10 --nvenc --h264 --yt --shorts --speed 5 --shortest
REM ------------------------

if "%~1"=="" (
  echo Drag and drop video files onto this .bat to process them.
  echo Or run: make_shorts.bat "clip1.mp4" "clip2.mp4" ...
  pause
  exit /b
)

for %%F in (%*) do (
  set "IN=%%~fF"
  set "OUT=%%~dpnF_shorts.mp4"
  echo Processing: "%%~nxF"
  python "siege_montage_maker.py" -i "!IN!" -o "!OUT!" --music "!MUSIC!" !FLAGS!
  if errorlevel 1 (
    echo Failed: "%%~nxF"
  ) else (
    echo Done: "!OUT!"
  )
)
echo All done.
pause
