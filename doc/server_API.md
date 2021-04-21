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
| get_modules | GET | Get list of modules managed by the user |
| add_module | POST | Adds new module to user account |
| remove_module | DELETE | Removes given module from the account |
| create_whitelist | POST | Create empty whitelist |
| get_all_whitelists | GET | Get list of all whitelists |
| get_module_all_whitelists | GET | Get list of all whitelists for a module |
| get_whitelisted_plates | GET | Get list of authored plates for given whitelist  |
| add_to_whitelist | POST | Add plate to whitelist |
| remove_from_whitelist| DELETE | Remove given plate from whitelist |
| remove_whitelist| DELETE | Remove given whitelist |
| bind_whitelist_to_module| POST | Add whitelist to a given module |
| unbind_whitelist_from_module| DELETE | Removes whitelist from given module |


## get_modules
### Call
``` GET /get_modules/```
### Exmaple result
```json
{
  "modules":[
    {
      "name": "ModuleA",
      "id":5
    },
    {
      "name": "ModuleB",
      "id":125
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
``` POST /add_module/ ```
### Body

```json
{
  "name":"ModuleName"
}   
```
On success: 
### Example result
```json
{
  "id":125
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
``` DELETE /remove_module?id=<ID>/ ```

### Error Codes
| Code | Message | 
| :-------- | :-------- |
| 204(No Content) | Successfully delted |
| 500 (Internal Server Error) | Server error|
| 404 (No Resource) | Module with such ID does not exist |

## create_whitelist
### Call
``` POST /create_whitelist/ ```
### Body

```json
{
  "name":"WhitelistName"
}   
```
On success: 
### Example result
```json
{
  "id":125
}   
```
### Error Codes
| Code | Message | 
| :-------- | :-------- |
| 200(OK) | Success |
| 500 (Internal Server Error) | Server error|
| 201 (Created) | Created whitelist |

## get_all_whitelists
### Call
``` GET /get_all_whitelists/ ```

### Example result
```json
{
    "whitelists": [
        {
            "id": 54,
            "name": "A",
            "plates": [
                "TKI12345",
                "DW123456"
            ]
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
``` GET /get_module_all_whitelists?id=<MODULE_ID>/ ```

### Example result
```json
{
    "whitelists": [
        {
            "id": 54,
            "name": "A",
            "plates": [
                "TKI12345",
                "DW123456"
            ]
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
``` GET /get_whitelisted_plates?id=<WHITELIST_ID>/ ```
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





## add_to_whitelist
### Call
``` POST /add_to_whitelist/ ```
### Body

```json
{
  "whitelist_id":12345,
  "plate":"DWR12345"
}   
```

### Error Codes
| Code | Message | 
| :-------- | :-------- |
| 200(OK) | Success |
| 500 (Internal Server Error) | Server error|
| 404 (Not Found) | Whitelist with such id does not exists |




## remove_from_whitelist
### Call
``` DELETE /remove_from_whitelist?id=<WHITELIST_ID>&plate=asgasg/ ```

### Error Codes
| Code | Message | 
| :-------- | :-------- |
| 204(No Content) | Success |
| 500 (Internal Server Error) | Server error|
| 404 (Not Found) | Whitelist with such id does not exists or plate not whitelisted |


## bind_whitelist_to_module
### Call
``` POST /bind_whitelist_to_module/ ```

### Body

```json
{
  "whitelist_id":12345,
  "module_id":"125116623"
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
``` POST /unbind_whitelist_from_module/ ```

### Body

```json
{
  "whitelist_id":12345,
  "module_id":"125116623"
}   
```

### Error Codes
| Code | Message | 
| :-------- | :-------- |
| 201(Created) | Success |
| 500 (Internal Server Error) | Server error|
| 404 (Not Found) | Whitelist with such id or module does not exists |

# Account management
## Prerequsites
User has no account. 
## Possible requests
| Name | Request | Description |
| :-------- | :-------- | :-------- |
| create_user | POST | Create new user with privided data |
| remove_user | DELETE| Removes user's account |
| change_email | POST | Changes user's email |
| change_password | POST | Changes user's password |



## create_user
### Call
``` POST /create_user/```
### Body
```json
{
  "user_data":[
    {
      "name": "John",
      "password":"John2137!",
	  "email":"john.doe@email.com"
    }
  ]
}   
```
### Example result
```json
{
  "Error": "email not valid"
}   
```


## Prerequsites
User is logged in. 
## remove_user
### Call
``` DELETE /remove_user?id=<ID>/ ```

### Example result
```json
{
  "Error": "ID is not valid"
}   
```

## change_email
### Call
``` POST /change_email/ ```
### Body

```json
{
  "user_id":12345,
  "new_email":"john12@example.com",
  "password":"X89bdhjk"
}   
```

### Example result
```json
{
  "Error": "0"
}   
```


## change_password

### Call
``` POST /change_password/ ```
### Body

```json
{
  "user_id":12345,
  "old_password":"X89bdhjk",
  "new_password":"8913nhoJ"
}   
```

### Example result
```json
{
  "Error": "old password is not valid"
}   
```











