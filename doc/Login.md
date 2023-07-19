## Authorization using a JWT (JSON Web Token).

## Login

-   URL: https://prod-chat.duckdns.org/api/login/
-   Request: Post(URL, {username, password}).  
    __The username field can contain a username or email__.

    ```
    URL = "https://prod-chat.duckdns.org/api/login/"
    data = {"username": "user@gmail.com",
            "password": "UserPassword"}

    response = request.post(URL, data)
    ```

    ```
    URL = "https://prod-chat.duckdns.org/api/login/"
    data = {"username": "userName",
            "password": "UserPassword"}

    response = request.post(URL, data)
    ```

-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```json
        {
            "Success": "Login successfully",
            "user": {
                "id": 1,
                "username": "userName",
                "email": "user@gmail.com",
                "is_email_confirmed": false/true
            }
        }
        ```

-   Unsuccessful response:
    -   Status code: 404 Not Found (user).
    -   Response body:

        ```json
        {
            "Invalid": "Invalid username or password"
        }
        ```

-   Additional information:  
    Upon successful user login, the access token is set in cookies as HttpOnly=True

    ```
    access_token = access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg5ODUyODEzLCJpYXQiOjE2ODk3NjY0MTMsImp0aSI6ImY1ZGZlY2NkM2FkNzQ5YTc4Zjg4OWIyNDhjNDBjYWJmIiwidXNlcl9pZCI6Mzl9.Rswt9Iss_WmtpSgV8hVi798NYv7Xz69r0Z1_BMnJ9pQ; 
    Path=/; 
    HttpOnly;
    ```

    -   The access token expires after 1 day.
    -   If you send __the wrong or expired access token__, when a token is needed, you get the following error with Status code 401 Unauthorized:

        ```json
        {
            "detail": "Given token not valid for any token type",
            "code": "token_not_valid",
            "messages": [
                 {
                    "token_class": "AccessToken",
                    "token_type": "access",
                     "message": "Token is invalid or expired"
                }
            ]
        }
        ```