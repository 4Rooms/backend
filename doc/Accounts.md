# Accounts App Documentation

## User registration
![img.png](img/register.png)
-   URL: https://prod-chat.duckdns.org/api/register/
-   Request: Post(URL, {email, password}).  
    Request doesn't require any token in headers.

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

        ```
        {
            "username": "userName",
            "email": "user@gmail.com",
            "is_email_confirmed": false
        }
        ```

-   Unsuccessful responses:
    -   Status code: 400 Bad Request.
    -   Response body:

        ```
        {
            "error": [
                "This password is too short. It must contain at least 8 characters.",
                "This password is too common.",
                "This password is entirely numeric."
            ]
        }
        ```

        ```
        {
            "username": [
                "user with this login already exists."
            ],
            "email": [
                "user with this email already exists."
            ]
        }
        ```

        ```
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

        ```
        {
            "email": [
                "Enter a valid email address."
            ]
        }
        ```

-   Additional information:  
    In case of a response with a status code of 201, the user will be sent a link to confirm his email. If the user follows the link, the value of the variable is_email_confirm will change to True.

## Authorization using a JWT (JSON Web Token).

## Login

![img_1.png](img/login.png)

-   URL: https://prod-chat.duckdns.org/api/token/
-   Request: Post(URL, {username, password}).  
    __The username field can contain a username or email__.  
    Request doesn't require any token in headers.

    ```
    URL = "https://prod-chat.duckdns.org/api/token/"
    data = {"username": "user@gmail.com",
            "password": "UserPassword"}
    response = request.post(URL, data)
    ```

    ```
    URL = "https://prod-chat.duckdns.org/api/token/"
    data = {"username": "userName",
            "password": "UserPassword"}
    response = request.post(URL, data)
    ```

-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```
        {
            "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4ODIxMTEzMiwiaWF0IjoxNjg3MzQ3MTMyLCJqdGkiOiIxMDBkODBlYzgzNTg0ZGI1YmExODQ5Njc3ODg0OWNjYSIsInVzZXJfaWQiOjEzfQ.aL849Cdf-s8htmOjimA9fqQ643in3K7kO_YeNbNzGmM",
            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg3NDMzNTMyLCJpYXQiOjE2ODczNDcxMzIsImp0aSI6Ijk4MGM3MjU4ZTNmMDQ4NmViZmU3OTMxYzBkMmQzMGIzIiwidXNlcl9pZCI6MTN9.wwT_HBIP_e9gUFLIL7emd4H8xf75GM8jKskdihnRlu4"
        }
        ```

-   Unsuccessful response:
    -   Status code: 401 Unauthorized.
    -   Response body:

        ```
        {
            "detail": "No active account found with the given credentials"
        }
        ```

-   Additional information:  
    We should save JWT because to authenticate the user in requests that require authentication, the access token key must be included in the Authorization HTTP header. The access token must be prefixed with the string literal "Bearer", with spaces separating the two strings.

    ```
    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg3NDMzNTMyLCJpYXQiOjE2ODczNDcxMzIsImp0aSI6Ijk4MGM3MjU4ZTNmMDQ4NmViZmU3OTMxYzBkMmQzMGIzIiwidXNlcl9pZCI6MTN9.wwT_HBIP_e9gUFLIL7emd4H8xf75GM8jKskdihnRlu4"
    headers = {"Authorization": "Bearer " + access_token}
    ```

    -   The access token expires after 1 day.
    -   The refresh token expires after 10 day.
    -   We can easily persist users between refreshes and login without any credentials. Whenever a token expires or a user refreshes we can get a new access token by sending a request to refresh token.
    -   If you send the wrong access token, when a token is needed, you get the following error with Status code 401 Unauthorized:

        ```
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

## Refresh token
![img_1.png](img/refresh.png)
-   URL: https://prod-chat.duckdns.org/api/token/refresh/
-   Request: Post({"refresh": "eyJhbGciOiJ..."}).  
    Request doesn't require any token in headers. __Request requires refresh token in data__.

    ```
    URL = "https://prod-chat.duckdns.org/api/token/refresh/"
    data = {"refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4ODIxMTEzMiwiaWF0IjoxNjg3MzQ3MTMyLCJqdGkiOiIxMDBkODBlYzgzNTg0ZGI1YmExODQ5Njc3ODg0OWNjYSIsInVzZXJfaWQiOjEzfQ.aL849Cdf-s8htmOjimA9fqQ643in3K7kO_YeNbNzGmM"}
    response = request.post(URL, data)
    ```

-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```
        {
            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg3NDM1OTU0LCJpYXQiOjE2ODczNDcxMzIsImp0aSI6IjkwM2FhNmRhNjhjZDQxZGY4ZjNhODYzNGY5MzhkNzc3IiwidXNlcl9pZCI6MTN9.TDFu-WU9shZr0VvpGOkGadMysavc5nKxDxR8ASxeaWs"
        }
        ```

-   Unsuccessful response:
    -   Status code: 401 Unauthorized.
    -   Response body:

        ```
        {
            "detail": "Token is invalid or expired",
            "code": "token_not_valid"
        }
        ```

## Get the current user info
![img.png](img/get_user.png)
-   URL: https://prod-chat.duckdns.org/api/user/
-   Request: Get(URL, headers={"Authorization": "Bearer " + access_token}).  
    Request requires access token in headers.

    ```
    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg3NDM1OTU0LCJpYXQiOjE2ODczNDcxMzIsImp0aSI6IjkwM2FhNmRhNjhjZDQxZGY4ZjNhODYzNGY5MzhkNzc3IiwidXNlcl9pZCI6MTN9.TDFu-WU9shZr0VvpGOkGadMysavc5nKxDxR8ASxeaWs"
    headers = {"Authorization": "Bearer " + access_token}
    response = request.get(URL, headers)
    ```

-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```
        {
            "username": "userName",
            "email": "user@gmail.com",
            "is_email_confirmed": false/true
        }
        ```

-   Unsuccessful response:
    -   Status code: 401 Unauthorized.
    -   Response body:

        ```
        {
            "detail": "Authorization header must contain two space-delimited values",
            "code": "bad_authorization_header"
        }
        ```

## Set/Get user avatar
-   URL: https://prod-chat.duckdns.org/api/profile/avatar/
-   Requests:
    -   Get(URL, headers={"Authorization": "Bearer " + access_token})
    -   Put(URL, headers={"Authorization": "Bearer " + access_token}, data={"avatar": file.jpg})
-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```
         {
            "avatar": "https://prod-chat.duckdns.org/media/avatars/dog2jpg-dog2.jpg"
         }
        ```

-   Unsuccessful response:
    -   Status code: 400 Bad Request.
    -   Response body:

        ```
        {
            "avatar": [
            "Upload a valid image. The file you uploaded was either not an image or a corrupted image."
            ]
        }
        ```

## Change password
-   URL: https://prod-chat.duckdns.org/api/user/change-password
-   Requests:
    -   Put(URL, headers={"Authorization": "Bearer " + access_token}, data={oldPassword, newPassword})
-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```
         {
            "message": "Password updated successfully"
         }
        ```

-   Unsuccessful responses:
    -   Status code: 400 Bad Request.
      -   Response body:

          ```
          {
              "old password error": [
                  "Old password is wrong"
              ]
          }
          ```

          ```
          {
              "new password error": [
              "This password is too short. It must contain at least 8 characters.",
              "This password is too common.",
              "This password is entirely numeric."
              ]
          }
          ```