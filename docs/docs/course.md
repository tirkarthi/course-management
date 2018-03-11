# API

## Get all courses

Get all courses with student info

### Permissions

- Admin

### Endpoint

`GET /api/courses/`

### Success response

* status code - 200
* response

```
[
    {
        "availability": true,
        "enrolled_students": [
            {
                "email": "",
                "first_name": "v",
                "id": 3,
                "last_name": "v"
            }
        ],
        "id": 1,
        "limit": 5,
        "name": "a",
        "unregistered_students": []
    },
    {
        "availability": true,
        "enrolled_students": [
            {
                "email": "",
                "first_name": "v",
                "id": 3,
                "last_name": "v"
            }
        ],
        "id": 5,
        "limit": 5,
        "name": "c",
        "unregistered_students": []
    },
    {
        "availability": true,
        "enrolled_students": [],
        "id": 6,
        "limit": 5,
        "name": "v",
        "unregistered_students": [
            {
                "email": "",
                "first_name": "v",
                "id": 3,
                "last_name": "v"
            }
        ]
    }
]
```

## Create a new course

Create a new course

### Permissions

- Admin

### Endpoint

`POST /api/courses/`


### Payload

```
{
	"name": "test"
}
```

### Success response

* status code - 201
* response

```
{
    "availability": true,
    "enrolled_students": [],
    "id": 7,
    "limit": 5,
    "name": "test",
    "unregistered_students": [
        {
            "email": "",
            "first_name": "v",
            "id": 3,
            "last_name": "v"
        }
    ]
}

```

### Error response

* status code - 400
* response

```
{
	"name": ["course with this name already exists."]
}

```

## Add user to a course

Add student to a course

### Permissions

- Admin


### Endpoint

`POST /api/courses/add_user/`


### Payload

```
{
	"course_id": 1,
	"student_id": 1
}
```

### Success response

* status code - 200
* response

```
{}
```

## Remove student from a course

Remove student from a course

### Permissions

- Admin

### Endpoint

`POST /api/courses/remove_user/`


### Payload

```
{
	"course_id": 1,
	"student_id": 1
}
```

### Success response

* status code - 200
* response

```
{}
```
