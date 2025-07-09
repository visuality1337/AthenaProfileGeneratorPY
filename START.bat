@echo off
title AthenaGeneratorPY created by github.com/visuality1337.

ECHO Installing the required packages for AthenaGeneratorPY!
TIMEOUT 3

py -3 -m pip install -U -r requirements.txt

CLS
ECHO Starting the bot...

py index.py
cmd /k