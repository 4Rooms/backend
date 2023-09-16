# Accounts


## Get the current user info (username, email, is_email_confirmed)
-   URL: /api/user/
-   Request: Get(URL).  

    ```
    response = request.get(URL)
    ```

-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```json
        {
            "Success": "Login successfully",
            "user": {
                "id": 6,
                "username": "user1",
                "email": "user1@gmail.com",
                "is_email_confirmed": true
            }
        }
        ```

-   Unsuccessful response:
    -   Status code: 401 Unauthorized, 403 Forbidden (if cookies is Empty, without access_token or token expire).  
        The same responses (401, 403) could be in other API as failed authorization or lack of access.
    -   Response body:

        ```json
        {
            "detail": "Authorization header must contain two space-delimited values",
            "code": "bad_authorization_header"
        }
        ```
        
        ```json
        {
            "type": "client_error",
             "errors": [
                {
                    "code": "permission_denied",
                    "detail": "You do not have permission to perform this action.",
                    "attr": null
                }
            ]
        }
        ```
        
        ```json
        {
            "type": "client_error",
            "errors": [
                {
                    "code": "token_not_valid",
                    "detail": "Given token not valid for any token type",
                    "attr": "detail"
                },
                {
                    "code": "token_not_valid",
                    "detail": "token_not_valid",
                    "attr": "code"
                },
                {
                    "code": "token_not_valid",
                    "detail": "AccessToken",
                    "attr": "messages.0.token_class"
                },
                {
                    "code": "token_not_valid",
                    "detail": "access",
                    "attr": "messages.0.token_type"
                },
                {
                    "code": "token_not_valid",
                    "detail": "Token is invalid or expired",
                    "attr": "messages.0.message"
                }
            ]
        }
        ```
        
        ```json
        {
            "type": "client_error",
            "errors": [
                {
                    "code": "permission_denied",
                    "detail": "You do not have permission to perform this action.",
                    "attr": null
                }
            ]
        }
        ```

## Change username/email.
-   URL: /api/user/
-   Request: Put(URL, data).

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
-   URL: /api/profile/
-   Requests:
    -   Get(URL)
    -   Put(URL, data={"avatar": file.jpg})
-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```json
         {
            "avatar": ".../media/avatars/file.jpg"
         }
        ```

-   Unsuccessful response:
    -   Status code: 400 Bad Request.
    -   Response body:

        ```json
        {
            "type": "validation_error",
            "errors": [
                {
                    "code": "invalid_image",
                    "detail": "Upload a valid image. The file you uploaded was either not an image or a corrupted image.",
                    "attr": "avatar"
                }
            ]
        }
        ```

## Change password
-   URL: /api/user/change-password
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

          ```json (old password is wrong)
          {
              "type": "validation_error",
              "errors": [
                  {
                      "code": "invalid",
                      "detail": "Wrong password",
                      "attr": null
                  }
              ]
          }
          ```

          ```json
          {
              "type": "server_error",
              "errors": [
                  {
                      "code": "error",
                      "detail": "['This password is too short. It must contain at least 8 characters.', 'This password is too common.', 'This password is entirely numeric.']",
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
                       "code": "required",
                       "detail": "This field is required.",
                       "attr": "old_password"
                   },
                   {
                       "code": "required",
                       "detail": "This field is required.",
                       "attr": "new_password"
                   }
               ]
          }
          ```
