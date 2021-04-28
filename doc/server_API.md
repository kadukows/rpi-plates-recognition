# rpi-plates-recognition server APIs
This document contains technical specification for planned server APIs in this project.

## JSON specification
Please be aware that temporarily syntax for documenting jsons structures is
simplification of [js-schema](https://github.com/molnarg/js-schema/). This may
change in the future.

# Module management
## Prerequsites
User is logged in.
## Possible requests
| Name | Request | Description |
| :-------- | :-------- | :-------- |
| [get_modules :white_check_mark:](#get_modules) | GET | Get list of modules managed by the user |
| [add_module :white_check_mark:](#add_module) | POST | Adds new module to user account |
| [remove_module :white_check_mark:](#remove_module) | DELETE | Removes given module from the account |
| [create_whitelist :white_check_mark:](#create_whitelist) | POST | Create empty whitelist |
| [get_all_whitelists :white_check_mark:](#get_all_whitelists) | GET | Get list of all whitelists created by user |
| [get_module_all_whitelists](get_module_all_whitelists) | GET | Get list of all whitelists for a module |
| [get_whitelisted_plates :white_check_mark:](#get_whitelisted_plates) | GET | Get list of authored plates for given whitelist owned by user  |
| [get_whitelists_for_plate](#get_whitelists_for_plate) | GET | Get list of whitelists owned by current user which contain given plate  |
| [add_plate_to_whitelist](#add_plate_to_whitelist) | POST | Add plate to whitelist owned by current user |
| [remove_plate_from_whitelist](#remove_plate_from_whitelist) | DELETE | Remove given plate from whitelist owned by current user|
| [remove_whitelist](#remove_whitelist) | DELETE | Remove given whitelist owned by current user|
| [bind_whitelist_to_module](#bind_whitelist_to_module) | POST | Add whitelist to a given module which is owned by current user|
| [unbind_whitelist_from_module](#unbind_whitelist_from_module) | DELETE | Removes whitelist from given module owned by current user|
| [add_plate_to_all_whitelists](#add_plate_to_all_whitelists) | POST | Add plate to all whitelists owned by current user|
| [remove_plate_from_all_whitelists](#remove_plate_from_all_whitelists) | DELETE | Removes plate from all whitelists owned by current user|


## get_modules
### Call
``` GET /api/get_modules```
### Exmaple result
```json
{
  "modules":[
    {
      "unique_id": "ModuleA",
    },
    {
      "unique_id": "ModuleB",
    }
  ]
}
```
### Error Codes
| Code | Message |
| :-------- | :-------- |
| 200(OK) | List prepared correctly |
| 500 (Internal Server Error) | Unable to prepare modules list|



## add_module
### Call
``` POST /api/add_module ```
### Body

```json
{
  "unique_id":"ModuleName"
}
```

### Error Codes
| Code | Message |
| :-------- | :-------- |
| 200(OK) | Success |
| 500 (Internal Server Error) | Server error|
| 201 (Created) | Created resource |

## remove_module
### Call
``` DELETE /api/remove_module?id=<UNIQUE_ID> ```

### Error Codes
| Code | Message |
| :-------- | :-------- |
| 204(No Content) | Successfully delted |
| 500 (Internal Server Error) | Server error|
| 404 (No Resource) | Module with such ID does not exist |
| 412 (Precondition failed) | Module with such ID is bound to another user|


## create_whitelist
### Call
``` POST /api/create_whitelist ```
### Body

```json
{
  "whitelist_name":"WhitelistName"
}
```
### Error Codes
| Code | Message |
| :-------- | :-------- |
| 200(OK) | Success |
| 500 (Internal Server Error) | Server error|
| 201 (Created) | Created whitelist |
| 418 (I'm a teapot :) ) | Whitelist with such name already exists |

## get_all_whitelists
### Call
``` GET /api/get_all_whitelists ```

### Example result
```json
{
    "whitelists": [
        {
            "whitelist_name": "A",
        },
        {
            "whitelist_name": "B",
        }
    ]
}
```
### Error Codes
| Code | Message |
| :-------- | :-------- |
| 200(OK) | Success |
| 500 (Internal Server Error) | Server error|

## get_module_all_whitelists
### Call
``` GET /api/get_module_all_whitelists?id=<MODULE_UNIQUE_ID> ```

### Example result
```json
{
    "whitelists": [
        {
            "whitelist_name": "A",
        },
        {
            "whitelist_name": "B",
        }
    ]
}
```
### Error Codes
| Code | Message |
| :-------- | :-------- |
| 200(OK) | Success |
| 500 (Internal Server Error) | Server error|
| 404 (Not Found) | Module with such id not found|



## get_whitelisted_plates
### Call
``` GET /api/get_whitelisted_plates?id=<WHITELIST_NAME> ```
### Example result

```json
{
    "plates": [
        "TKI1244",
        "DW12515"
    ]
}
```
### Error Codes
| Code | Message |
| :-------- | :-------- |
| 200(OK) | Success |
| 500 (Internal Server Error) | Server error|
| 404 (Not Found) | Whitelist with such id does not exists |



## get_whitelists_for_plate
### Call
``` GET /api/get_whitelists_for_plate?plate=<PLATE> ```
### Example result
```json
{
    "whitelists": [
        {
            "whitelist_name": "A",
        },
        {
            "whitelist_name": "B",
        }
    ]
}
```
### Error Codes
| Code | Message |
| :-------- | :-------- |
| 200(OK) | Success |
| 500 (Internal Server Error) | Server error|
| 404 (Not Found) | No whitelists for plate found |






## add_plate_to_whitelist
### Call
``` POST /api/add_plate_to_whitelist ```
### Body

```json
{
  "whitelist_name":12345,
  "plate":"DWR12345"
}
```

### Error Codes
| Code | Message |
| :-------- | :-------- |
| 200(OK) | Success |
| 500 (Internal Server Error) | Server error|
| 404 (Not Found) | Whitelist with such id does not exists |
| 400 (Bad request) | Plate is not properly formatted |





## remove_plate_from_whitelist
### Call
``` DELETE /api/remove_plate_from_whitelist?id=<WHITELIST_NAME>&plate=<PLATE> ```

### Error Codes
| Code | Message |
| :-------- | :-------- |
| 204(No Content) | Success |
| 500 (Internal Server Error) | Server error|
| 404 (Not Found) | Whitelist with such id does not exists |
| 428 (Precondition required) | Plate not whitelisted |


## bind_whitelist_to_module
### Call
``` POST /api/bind_whitelist_to_module ```

### Body

```json
{
  "whitelist_name":12345,
  "module_unique_id":"125116623"
}
```

### Error Codes
| Code | Message |
| :-------- | :-------- |
| 201(Created) | Success |
| 500 (Internal Server Error) | Server error|
| 404 (Not Found) | Whitelist with such id or module does not exists |


## unbind_whitelist_from_module
### Call
``` POST /api/unbind_whitelist_from_module ```

### Body

```json
{
  "whitelist_name":12345,
  "module_unique_id":"125116623"
}
```

### Error Codes
| Code | Message |
| :-------- | :-------- |
| 201(Created) | Success |
| 500 (Internal Server Error) | Server error|
| 404 (Not Found) | Whitelist with such id or module does not exists |


## add_plate_to_all_whitelists
### Call
``` POST /api/add_plate_to_whitelist ```
### Body

```json
{
  "plate":"DWR12345"
}
```

### Error Codes
| Code | Message |
| :-------- | :-------- |
| 200(OK) | Success |
| 500 (Internal Server Error) | Server error|
| 404 (Not Found) | No whitelist exists |
| 400 (Bad request) | Plate is not properly formatted |



## remove_plate_from_all_whitelists
### Call
``` DELETE /api/remove_plate_from_all_whitelists?plate=asgasg ```

### Error Codes
| Code | Message |
| :-------- | :-------- |
| 200(OK) | Success |
| 500 (Internal Server Error) | Server error|
| 404 (Not Found) | No whitelist exists |
| 400 (Bad request) | Plate is not properly formatted |
