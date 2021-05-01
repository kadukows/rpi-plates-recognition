# rpi-plates-recognition
RPi project that includes recognition of plates using machine learning and
RESTful API for use with mobile app.

## Setting up
To run flask server and other utilities this project requires 1st time set up.
After cloning and cd'ing into repo:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
This installs all appropriate packages into venv, and needs to be done only once.

After that, each time you log into new terminal you need to activate venv with
`source venv/bin/activate` and export some Flask variables to your current
shell:
```
export FLASK_APP='rpiplatesrecognition'
export FLASK_ENV='development'
```
This tells flask what package it should run with `flask run` command.

## Initializing database
| Command | Result |
| ------- | ------ |
| `flask init-db` | Initializes empty database |
| `flask init-db-debug` | Initialized db with default values |

## Running a server
After 1st time set up flask server could be run by:
```
flask run
```
Webserver is accessible at http://127.0.0.1:5000

For accessing server from another device on LAN (e.g. a smartphone) you need
to modify run command to `flask run -h 0.0.0.0`.

## Swagger API documentation
Swagger API documentation is available at `/api/ui` route.

## Runing unit tests
To run unit tests, simply run `pytest` from root directory of repo.
