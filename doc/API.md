# rpi-plates-recognition API
This document contains technical specification for planned API in this project.

## JSON specification
Please be aware that temporarily syntax for documenting jsons structures is
simplification of [js-schema](https://github.com/molnarg/js-schema/). This may
change in the future.


# Requests

## Entry permit (NYI)
### Request structure
RPi will start "photo -> acqusition -> access decision" routine upon receiving
specific GET request:
```
GET /api/take_photo
```
This request will return JSON object describing result of this routine:
```
{
    "plates-recognized": Boolean,
    "access-permit": Boolean,
    "gate-will-open": Boolean,
    "access-token": String
}
```
where `plates-recognized` is set to `true` if any plates were recognized in
picture, `access-permit` is set to `true` if plates recognized in picture are
in whitelist, `gate-will-open` is set to `true` if gate will be opened for
user and `access-token` field is 32 character random string if acces is granted,
or empty if not.

### Example
1. Successful request.
```json
{
    "plates-recognized": true,
    "access-permit": true,
    "gate-will-open": true,
    "access-token": "8849e174cf00a0065868069cf5c54c70"
}
```

2. Plates were not recognized in image.
```json
{
    "plates-recognized": false,
    "access-permit": false,
    "gate-will-open": false,
    "access-token": ""
}
```

3. Plates were recognized, but aren't in the whitelist.
```json
{
    "plates-recognized": true,
    "access-permit": false,
    "gate-will-open": false,
    "access-token": ""
}
```

4. Plates were recognized and they are in whitelist, but gate is busy (i.e.
another car is going in or goint out).
```json
{
    "plates-recognized": true,
    "access-permit": true,
    "gate-will-open": false,
    "access-token": ""
}
```


## Exit request (NYI)
### Request structure
RPi should also let users that are already in the property out. This should be
achieved by unique token issued to each user upon entering property. This token
should act as one time exit permit. RPi will open the gate upon receiving
specific GET request:
```
GET /api/exit?token="<user's token goes here>"
```
where token is `access-token` issued to each user upon entering. This request
will return JSON object:
```
{
    "exit-permit": Boolean,
    "gate-will-open": Boolean
}
```
where `exit-permit` is set to `true` if token were recognized, and
`gate-will-open` is set to `true` if gate is not busy. Please note that token
is not spend if `exit-permit` is set to `true`, but `gate-will-open` is set to
`false`.

### Example
1. Sucessful request.
```json
{
    "exit-permit": true,
    "gate-will-open": true
}
```

2. Token was recognized, but gate is busy (i.e. another car tries to access
property). Token can be reused.
```json
{
    "exit-permit": true,
    "gate-will-open": false
}
```

3. Token was not recognized.
```json
{
    "exit-permit": false,
    "gate-will-open": false
}
```
