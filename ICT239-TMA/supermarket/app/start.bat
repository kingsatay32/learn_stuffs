@echo off
set FLASK_APP=app.py
set PYTHONPATH=.
set FLASK_DEBUG=1
flask run --host=0.0.0.0