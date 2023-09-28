# 4Rooms

## Authentication

### JWT vs Session

<details>
  <summary>Pros and Sons</summary>

#### JWT

JWT (JSON Web Tokens) and Session are both methods used to manage user authentication and authorization in web applications, but they have distinct characteristics and usage scenarios.

It is often used for stateless authentication and is passed as a header or a query parameter in HTTP requests.

The token contains claims (information) about the user and is digitally signed, ensuring its integrity and authenticity.

Since JWTs are self-contained, server-side storage is not required, making them ideal for scalability and stateless architectures.

#### Session

Sessions involve server-side storage of user data, usually in memory or a database, associated with a unique session identifier (usually stored in a cookie on the client-side).

When a user logs in, the server creates a session, assigns a session ID to the user, and stores relevant user information in the server's memory or database.

The session ID is sent to the client as a cookie, and subsequent requests from the client include this session ID, allowing the server to identify the user and retrieve their data from the session store.
Sessions can be invalidated or terminated by the server, making it easier to manage user access and log out users if necessary.

</details>

We decided to use JWT for authentication.


### Storing JWT in cookie vs local storage

<details>
  <summary>Pros and Cons</summary>

-   Storing JWTs in cookies is a common practice as it offers better security compared to local storage.
-   Cookies can be configured with the HttpOnly flag, which prevents client-side scripts from accessing the cookie. This protects the JWT from cross-site scripting (XSS) attacks.
-   Cookies can also be set with the Secure flag, ensuring they are only transmitted over HTTPS, enhancing their security further.
-   By setting the SameSite attribute to "Strict" or "Lax," it is possible to mitigate the risk of CSRF (Cross-Site Request Forgery) attacks.
-   However, when using cookies, there might be concerns about CSRF attacks, which can be addressed by implementing additional security measures like CSRF tokens.

-   Unlike cookies, local storage data is accessible by client-side scripts, which poses security risks, especially when dealing with sensitive information like JWTs.
-   Storing JWTs in local storage can expose them to XSS attacks, as malicious scripts could access and steal the token.
-   Local storage is not automatically sent in HTTP requests like cookies. Therefore, developers need to handle manually attaching the JWT to each request, increasing complexity.
-   While using local storage for JWTs might seem convenient, it is generally discouraged due to the security risks involved.

</details>

We decided to store JWT in cookie with HttpOnly flag and Secure flag.

## REST API

Web UI will communicate with the server via REST API for the following functions:

*   Account management
    -   Registration
    -   Login
*   Chat management
    -   Create chat
    -   Join chat
    -   Sort messages
    -   Search messages
    -   Message history

## Websocket API

Web UI will communicate with the server via Websocket API for the following functions:

*   Messaging
    -   Send message
    -   Receive message
    -   Edit message
*   Typing indicator

### Data format

#### Message

```json
{
    "id": 11,
    "timestamp": "1692478065",
    "user_name": "user3",
    "user_avatar": "/media/avatar.jpg",
    "text": "Good book",
    "is_deleted": false,
    "chat": 1,
    "user": 3
}
```

-   If `messageId` is not provided, the server will generate a new one.
-   If `messageId` is provided, the server will update the message with the same `messageId`.

#### Typing indicator

```json
{
  "event_type": "typing_indicator",
  "userId": "string",
  "chatId": "string"
}
```

## API Documentation

### Possible error responses and their explanations

#### 400 Bad Request
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

#### 401 Unauthorized
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

#### 500 Internal Server Error
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

## WebSocket Events

#### Event chat_message
The event is sent to a group of users in the chat.

```json
{
  "message": {
    "id": 40,
    "user_name": "user3",
    "user_avatar": "/media/default-user-avatar.jpg",
    "text": "Message text",
    "timestamp": "2023-09-26T14:17:44.250236Z",
    "is_deleted": false,
    "chat": 1,
    "user": 3
  },
  "event_type": "chat_message",
  "timestamp": "2023-09-26T14:17:44.250236Z"
}
```

#### Event connected_user (the user joined to chat)
The event is sent to a group of users in the chat, except for yourself.

```json
{
  "event_type": "connected_user",
  "user": {
    "id": 1,
    "username": "user1",
    "avatar": "/media/avatars/ava.jpg"
  },
  "timestamp": "2023-09-26T14:17:44.250236Z"
}
```

#### Event disconnected_user (the user left the chat)
The event is sent to a group of users in the chat.

```json
{
  "event_type": "disconnected_user",
  "user": {
    "id": 1,
    "username": "user1",
    "avatar": "/media/avatars/ava.jpg"
  },
  "timestamp": "2023-09-26T14:17:44.250236Z"
}
```

#### Event online_user_list (list of users connected to a current chat)
The event will send a dictionary with a list of online users in this chat to the user who just joined the chat.  
The current user is not included in this list.

```json
{
  "event_type": "online_user_list",
  "user_list": [
    {
      "id": 1,
      "username": "user1",
      "avatar": "/media/avatars/avatar1.jpg"
    },
    {
      "id": 2,
      "username": "user2",
      "avatar": "/media/avatars/avatar2.jpg"
    }
  ],
  "timestamp": "2023-09-26T14:17:44.250236Z"
}
```