## API endpoints

API endpoints description is available [bellow](#/api)

## Possible error responses and their explanations

### 400 Bad Request
This is returned when the request is malformed or invalid. Here's how the response would look:

```json
{
    "type": "validation_error",
    "errors": [
        {
            "code": "invalid",
            "detail": "Enter a valid email address.",
            "attr": "email"
        }
    ]
}
```

### 401 Unauthorized
These errors are returned with the status code 401 whenever the authentication fails or a request is made to an
endpoint without providing the authentication information as part of the request. Here's how it looks like:
```json
{
    "type": "client_error",
    "errors": [
        {
            "code": "not_authenticated",
            "detail": "Authentication credentials were not provided.",
            "attr": null
        }
    ]
}
```

### 500 Internal Server Error
This is returned when the API server encounters an unexpected error. Here's how the response would look:

```json
{
    "type": "server_error",
    "errors": [
        {
            "code": "error",
            "detail": "A server error occurred.",
            "attr": null
        }
    ]
}
```
