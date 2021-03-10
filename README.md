# rpi-plates-recognition
RPi project that includes recognition of plates using machine learning, RESTful
API for use with mobile app and web application.

## Setting up
To run flask server and other utilities project requires 1st time set up.
```
git clone https://github.com/kadukows/rpi-plates-recognition
cd rpi-plates-recognition
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running a server
After 1st time set up flask server can be ran by simple:
```
cd src
flask run
```
Webserver is accessible at http://127.0.0.1:5000

For accessing server from another device on LAN (e.g. a smartphone) you need
to modify run command to `flask run -h 0.0.0.0`.
