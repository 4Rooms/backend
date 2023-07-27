# Accounts


## Get the current user info (username, email, is_email_confirmed")
-   URL: https://prod-chat.duckdns.org/api/user/
-   Request: Get(URL, headers={"Authorization": "Bearer " + access_token}).  
    Request requires access token in headers.

    ```
    response = request.get(URL)
    ```

-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```json
        {
            "username": "userName",
            "email": "user@gmail.com",
            "is_email_confirmed": false/true
        }
        ```

-   Unsuccessful response:
    -   Status code: 401 Unauthorized.
    -   Response body:

        ```json
        {
            "detail": "Authorization header must contain two space-delimited values",
            "code": "bad_authorization_header"
        }
        ```

## Change username / email.
-   URL: https://prod-chat.duckdns.org/api/user/
-   Request: Put(URL, headers={"Authorization": "Bearer " + access_token}, data={username, email}).  
    Request requires access token in headers.

    ```
    data = {"username": "userName", "email": "userEmail"}
    response = request.put(URL, data)
    ```

-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```json
        {
            "message": "Email, Username updated successfully"
        }
        ```

-   Unsuccessful response:
    -   Status code: 400 Bad Request.
    -   Response body:

        ```json
        {
            "email": [
                "Enter a valid email address."
            ]
        }
        ```

        ```json
        {
            "username error": "That username already registered"
        }
        ```

        ```json
        {
            "email error": "That email already exists"
        }
        ```

## Set/Get user profile (avatar)
-   URL: https://prod-chat.duckdns.org/api/profile/
-   Requests:
    -   Get(URL)
    -   Put(URL, data={"avatar": file.jpg})
-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```json
         {
            "avatar": "https://prod-chat.duckdns.org/media/avatars/file.jpg"
         }
        ```

-   Unsuccessful response:
    -   Status code: 400 Bad Request.
    -   Response body:

        ```json
        {
            "avatar": [
            "Upload a valid image. The file you uploaded was either not an image or a corrupted image."
            ]
        }
        ```

## Change password
-   URL: https://prod-chat.duckdns.org/api/user/change-password
-   Requests:
    -   Put(URL, data={oldPassword, newPassword})
-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```json
         {
            "message": "Password updated successfully"
         }
        ```

-   Unsuccessful responses:
    -   Status code: 400 Bad Request.
      -   Response body:

          ```json
          {
              "old password error": [
                  "Old password is wrong"
              ]
          }
          ```

          ```json
          {
              "new password error": [
              "This password is too short. It must contain at least 8 characters.",
              "This password is too common.",
              "This password is entirely numeric."
              ]
          }
          ```