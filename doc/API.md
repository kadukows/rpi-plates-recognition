# rpi-plates-recognition API
This document contains technical specification for planned API in this project.

## JSON specification
Please be aware that temporarily syntax for documenting jsons structures is
simplification of [js-schema](https://github.com/molnarg/js-schema/). This may
change in the future.

## Latest photos + possible recognised plates
User can request X latest photos by GET request denoted below:
```
GET /latest_photos?start=X&count=Y
GET /latest_photos?from=Z&count=Y
```
First version requests Y last photos offseted by X. For example, request
`GET /latest_photos?start=0&count=20` would return 20 last photos, and
`GET /latest_photos?start=21&count=20` would return next 20 photos.

Second version requests Y last photos from timestamp Z. Z should be formatted
as number of seconds passed from 1 January 1970. For example, request
`GET /latest_photos?from=1615385401&count=20` would return 20 photos starting
from first photo took after 10.03.2021 15:10:01.

#### Server response
In response server returns JSON object that consists of smaller objects:
- `Photo` object, describing photo that can be accessed on the server
    ```
    {
        "photo_id": Number,  // unqiue id for a photo, used for accessing photos later
        "timestamp": Number,  // date when photo was took (seconds from 1 Jan 1970)
        "?plates": String,  // if plates were detected in a photo, JSON object will contain this field
    }
    ```

JSON object that is returned from a server looks like this:
```
{
    "success": Bool,  // if request succeeded
    "photo-plates": Array.of(Photo)  // array of Photo objects described previously
}
```

#### Example
Example server response could look like these:
```json
{
    "success": true,
    "photo-plate": [
        {
            "photo_id": 137,
            "timestamp": 1615385401
        },
        {
            "photo_id": 138,
            "timestamp": 1615385301
        },
        {
            "photo_id": 139,
            "timestamp": 1615385250,
            "plates": "DW4PH36"
        }
    ]
}
```

## Get photo url
User can request url of particular photo by GET request denoted below:
```
GET /get_photo?photo_id=X
```
Where X is the same photo id as in latest photos request.

#### Server response
JSON object that is returned from a server looks like this:
```
{
    "success": Bool,  // if request succeeded
    "?photo_url": String  // if requests suceeded, JSOn object will contain this url
}
```

### Example
```json
{
    "success": true,
    "photo_url": "https://i.kym-cdn.com/entries/icons/original/000/025/526/gnome.jpg"
}
```
