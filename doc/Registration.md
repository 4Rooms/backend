# Registration


## User registration
-   URL: https://prod-chat.duckdns.org/api/register/
-   Request: Post(URL, {username, email, password}).

    ```
    URL = "https://prod-chat.duckdns.org/api/register/"
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
            "error": [
                "This password is too short. It must contain at least 8 characters.",
                "This password is too common.",
                "This password is entirely numeric."
            ]
        }
        ```

        ```json
        {
            "password": [
                "This field may not be blank."
            ]
        }
        ```

        ```json
        {
            "username": [
                "user with this login already exists."
            ],
            "email": [
                "user with this email already exists."
            ]
        }
        ```

        ```json
        {
            "username": [
                "This field is required."
            ],
            "email": [
                "This field is required."
            ],
            "password": [
                "This field is required."
            ]
        }
        ```

        ```json
        {
            "email": [
                "Enter a valid email address."
            ]
        }
        ```

-   Additional information:  
    In case of a response with a status code of 201, the user will be sent a link to confirm his email. Link in mail: URL = http://<UIHost>/confirm-email/?token_id=<token>.  
    To confirm email and change the variable is_email_confirm to True you should do Get request to URL = https://prod-chat.duckdns.org/api/confirm-email/?token_id=<token>.