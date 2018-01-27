@echo off
cd /d %~dp0
python FFmpegConveter.py -i %1 -s 21
pause
