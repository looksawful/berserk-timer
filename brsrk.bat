@echo off
python setup.py
py -m src.main 25 -w %*
pause


