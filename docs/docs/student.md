# API

## Get courses for a user

### Permissions

- Authenticated user

### Endpoint

`GET /api/users/courses/`

### Response

```
{
    "available": [
        {
            "availability": true,
            "id": 7,
            "limit": 5,
            "name": "test"
        }
    ],
    "enrolled": [
        {
            "availability": true,
            "id": 1,
            "limit": 5,
            "name": "a"
        },
        {
            "availability": true,
            "id": 5,
            "limit": 5,
            "name": "c"
        },
        {
            "availability": true,
            "id": 6,
            "limit": 5,
            "name": "v"
        }
    ]
}
```

## Enroll to a course

Enroll to a course

### Permissions

- Authenticated user


### Endpoint

`POST /api/users/enroll_course/`

### Payload

```
{
	"course": 7
}
```

### Response

```
{
    "availability": true,
    "id": 7,
    "limit": 5,
    "name": "test"
}

```

## Cancel a course

Cancel course enrollment

### Permissions

- Authenticated user

### Endpoint

`POST /api/users/cancel_course/`

### Payload

```
{
	"course": 7
}
```

### Response

```
{
    "availability": true,
    "id": 7,
    "limit": 5,
    "name": "test"
}

```
