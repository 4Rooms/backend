# Login


## User login
-   URL: /api/login/
-   Request: Post(URL, {username, password}).  
    __The username field can contain a username or email__.

    ```
    URL = "/api/login/"
    data = {"username": "user@gmail.com",
            "password": "UserPassword"}

    response = request.post(URL, data)
    ```

    ```
    URL = "/api/login/"
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
                "is_email_confirmed": true
            }
        }
        ```

-   Unsuccessful response:
    -   Status code: 404 Not Found (user).
    
        Response body:

        ```json
        {
            "type": "validation_error",
            "errors": [
                {
                    "code": 404,
                    "detail": "Invalid username or password",
                    "attr": "Invalid"
                }
            ]
        }
        ```
    
    -   Status code: 400

        ```json
        {
            "type": "validation_error",
            "errors": [
                {
                    "code": "blank",
                    "detail": "This field may not be blank.",
                    "attr": "username"
                }
            ]
        }
        ```

-   Additional information:  
    After successful user login, the access token is set in cookies as HttpOnly=True

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

## Sign in With Google

### Authentication Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant Google

    User ->> Frontend: Click: Sign in With Google
    activate Frontend
    
    Frontend ->> Backend: Redirect: /oauth/login/google-oauth2/
    activate Backend

    Backend ->> Google: https://accounts.google.com/o/oauth2/auth
    activate Google

    Google ->> User: Confirm Sign in
    User ->> Google: Confirm: https://accounts.google.com/_/signin/oauth
    Google ->> Backend: Redirect: /oauth/complete/google-oauth2/
    deactivate Google

    activate Backend
    Backend ->> Backend: Create/Login user

    rect rgba(50, 100, 50, .4)
        Backend ->> Frontend: Redirect: /logged-in/
    end
    deactivate Backend

    Note left of Backend: Along with redirection<br />the backend sets the access<br />token in a cookie.

    Frontend ->> User: Show login result
    deactivate Backend
    deactivate Frontend
```

### Description

1.  The process begins with the user clicking the "Sign in With Google" button in the web application's interface.
2.  The frontend redirects user to `/oauth/login/google-oauth2/`.
3.  The backend, responsible for handling authentication interactions, receives the request from the frontend.
4.  The backend initiates an authentication request to Google's OAuth 2.0 service by making a request to `https://accounts.google.com/o/oauth2/auth`.
5.  Google's OAuth service prompts the user to confirm their login. The user interacts with this confirmation screen.
6.  The user confirms the login, and this acknowledgment is sent back to Google's service at `https://accounts.google.com/_/signin/oauth`.
7.  With the user's confirmation, Google's service generates an authentication response and sends a redirection request to the backend at `/oauth/complete/google-oauth2/`.
8.  The backend receives the authentication response from Google's service and creates a new user or logs in an existing user.
9.  The backend, upon successful completion, redirects the flow back to the frontend through the URL `/logged-in/` and sets the access token in a cookie.
10. The frontend processes the completion signal from the backend and displays the login result to the user.
    This result could be a success message or a notification confirming successful login using their Google account.
