# Registration


## User registration
-   URL: /api/register/
-   Request: Post(URL, {username, email, password}).

    ```
    URL = "/api/register/"
    data = {"username": "userName",
            "email": "user@gmail.com",
            "password": "userPassword"}

    response = request.post(URL, data)
    ```

-   Successful response:
    -   Status code: 201.
    -   Response body:

        ```json
        {
            "id": 1,
            "username": "userName",
            "email": "user@gmail.com",
            "is_email_confirmed": false
        }
        ```

-   Unsuccessful responses:
    -   Status code: 400 Bad Request.
    -   Response body:

        ```json
        {
            "type": "validation_error",
            "errors": [
                {
                    "code": "invalid",
                    "detail": "This password is too short. It must contain at least 8 characters.",
                    "attr": null
                },
                {
                    "code": "invalid",
                    "detail": "This password is too common.",
                    "attr": null
                },
                {
                    "code": "invalid",
                    "detail": "This password is entirely numeric.",
                    "attr": null
                }
            ]
        }
        ```

        ```json
        {
            "type": "validation_error",
            "errors": [
                {
                    "code": "blank",
                    "detail": "This field may not be blank.",
                    "attr": "username"
                },
                {
                    "code": "blank",
                    "detail": "This field may not be blank.",
                    "attr": "email"
                },
                {
                    "code": "blank",
                    "detail": "This field may not be blank.",
                    "attr": "password"
                }
            ]
        }
        ```

        ```json
        {
            "type": "validation_error",
            "errors": [
                {
                    "code": "unique",
                    "detail": "user with this login already exists.",
                    "attr": "username"
                },
                {
                    "code": "unique",
                    "detail": "user with this email already exists.",
                    "attr": "email"
                }
            ]
        }
        ```

        ```json
        {
            "type": "validation_error",
            "errors": [
                {
                    "code": "required",
                    "detail": "This field is required.",
                    "attr": "username"
                },
                {
                    "code": "required",
                    "detail": "This field is required.",
                    "attr": "email"
                },
                {
                    "code": "required",
                    "detail": "This field is required.",
                    "attr": "password"
                }
            ]
        }
        ```

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
        
        ```json
        {
            "type": "validation_error",
            "errors": [
                {
                    "code": "max_length",
                    "detail": "Ensure this field has no more than 128 characters.",
                    "attr": "password"
                }
            ]
        }
        ```

-   Additional information:  
    In case of a response with a status code of 201, the user will be sent a link to confirm his email. Link in mail: URL = http://<UIHost>/confirm-email/?token_id=<token>.
    To confirm email and change the variable is_email_confirm to True you should do Get request to URL = /api/confirm-email/?token_id=<token>.
    -   You can't get/post... information if the email is unconfirmed. You will get the following error:

        ```json
         {
             "type": "client_error",
             "errors": [
                 {
                     "code": "permission_denied",
                     "detail": "The email address is unconfirmed.",
                     "attr": null
                 }
             ]
         }
        ```