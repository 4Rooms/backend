# Chat API


## Create chat
-   URL: https://prod-chat.duckdns.org/api/chat/<room>/
-   Request: Post(URL, data)  
    -   data: title, description (optional), img (optional)  
    -   chat titles cannot be repeated in the same room  
    -   __room__ must have one of the following string values:
        -   "films"
        -   "music"
        -   "books"
        -   "games"

    ```
    URL = "https://prod-chat.duckdns.org/api/chat/books/"
    data = {"title": "Harry Potter",
            "description": "Discussion of characters",
            "img": "file.jpeg"}

    response = request.post(URL, data)
    ```

-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```json
        {
            "chat": {
                "id": 3,
                "title": "Harry Potter",
                "room": "films",
                "img": "https://prod-chat.duckdns.org/media/file.jpg",
                "user": "userName",
                "description": "Discussion of characters",
                "url": "/chat/films/3/",
                "timestamp": "2023-08-03T08:51:26.593514Z"
            }
        }
        ```
        __url__ - path for connection to chat by Websocket

-   Unsuccessful response:
    -   Status code: 400 Bad Request.
    -   Response body:

        ```json
        {
            "room": [
                "\"movie\" is not a valid choice."
            ]
        }
        ```

        ```json
        {
            "title": [
                "This field is required."
            ],
            "room": [
                "This field is required."
            ]
        }
        ```

        If the posted title is used in the current room

        ```json
        {
            "non_field_errors": [
            "The fields room, title must make a unique set."
            ]
        }
        ```

        ```json
        {
            "description": [
                "Ensure this field has no more than 400 characters."
            ],
            "title": [
                "Ensure this field has no more than 70 characters."
            ]
        }
        ```

## Get chats from the certain room
-   URL: https://prod-chat.duckdns.org/api/chat/<room>/
    -   __room__ must have one of the following string values:
        -   "films"
        -   "music"
        -   "books"
        -   "games"
-   Request: Get(URL)

    ```
    URL = "https://prod-chat.duckdns.org/api/chat/films/"
    response = request.post(URL)
    ```

-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```json
        {
            "count": 3,
            "next": null,
            "previous": null,
            "results": [
                {
                    "id": 1,
                    "title": "Harry Potter characters",
                    "room": "films",
                    "img": "https://prod-chat.duckdns.org/media/chat_img/Hurry.jpg",
                    "user": "user1",
                    "description": "Who is your favorite character?",
                    "url": "/chat/films/1/",
                    "timestamp": "2023-08-04T20:12:10.777701Z"
                },
                {
                    "id": 2,
                    "title": "The Lord of the Rings films",
                    "room": "films",
                    "img": "https://prod-chat.duckdns.org/media/chat_img/frodo.jpg",
                    "user": "user2",
                    "description": "Which film is the best in the series?",
                    "url": "/chat/films/2/",
                    "timestamp": "2023-08-04T20:14:30.256093Z"
                },
                {
                    "id": 3,
                    "title": "Friends",
                    "room": "films",
                    "img": "https://prod-chat.duckdns.org/media/chat_img/default.jpg",
                    "user": "user1",
                    "description": null,
                    "url": "/chat/films/3/",
                    "timestamp": "2023-08-04T20:23:54.859836Z"
                }
            ]
        }
        ```

    -   count - number of all records in DB
    -   next - link to get the next 100 records by Get request on it
    -   previous - link to get the previous 100 records by Get request on it
    -   results - 100 or fewer records from DB (100 or fewer chats)


-   Unsuccessful response:
    -   Status code: 400 Bad Request.
    -   Response body:

        ```json
        {
            "Error": "wrong room"
        }
        ```

## Update chat description
-   URL: https://prod-chat.duckdns.org/api/chat/<chatId>/
-   Request: Patch(URL)
    -   data: description

    ```
    URL = "https://prod-chat.duckdns.org/api/chat/10/"
    data = {"description": "Chat description"}
    response = request.post(URL, data)
    ```

-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```json
        {
            "id": 10,
            "title": "Imagine Dragons",
            "room": "music",
            "img": "https://prod-chat.duckdns.org/media/chat_img/file.jpg",
            "user": "Leslie",
            "description": "Chat description",
            "url": "/chat/music/10/",
            "timestamp": "2023-08-07T12:16:40.385811Z"
        }
        ```

-   Unsuccessful response:
    -   Status code: 400 Bad Request, 403 Forbidden (user isn't a creator of chat or user sent not description field).
    -   Response body:

        ```json
        {
            "type": "client_error",
            "errors": [
                {
                    "code": "permission_denied",
                    "detail": "The action is allowed only to the author",
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
                    "code": "permission_denied",
                    "detail": "Only the chat description can be changed",
                    "attr": null
                }
            ]
        }
        ```

        ```json
        {
            "description": [
                "Ensure this field has no more than 400 characters."
            ]
        }
        ```

## Delete chat
-   URL: https://prod-chat.duckdns.org/api/chat/<chatId>/
-   Request: Delete(URL)

    ```
    URL = "https://prod-chat.duckdns.org/api/chat/10/"
    response = request.delete(URL)
    ```

-   Successful response:
    -   Status code: 204 No Content.
    -   Response body: Empty.
-   Unsuccessful response:
    -   Status code: 404 Not Found (There is no chat with such ID), 403 Forbidden.
    -   Response body:

        ```json
        {
            "type": "client_error",
            "errors": [
                {
                    "code": "not_found",
                    "detail": "Not found.",
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
                    "code": "permission_denied",
                    "detail": "The action is allowed only to the author",
                    "attr": null
                }
            ]
        }
        ```

## Get message history from the chat
-   URL: https://prod-chat.duckdns.org/api/chat/<chat-id>/messages/
-   Request: Get(URL)

    ```
    URL = "https://prod-chat.duckdns.org/api/chat/10/messages/"
    response = request.get(URL)
    ```

-   Successful response:
    -   Status code: 204 No Content.
    -   Response body: Empty

        ```json
        {
            "count": 2,
            "next": null,
            "previous": null,
            "results": [
                {
                    "id": 1,
                    "timestamp": "2023-08-24T14:41:56.250209Z",
                    "user_name": "testuser",
                    "user_avatar": "/media/avatars/user1-avatar.png",
                    "text": "Hi",
                    "chat": 10,
                    "user": 1
                },
                {
                    "id": 2,
                    "timestamp": "2023-09-04T18:34:22.170972Z",
                    "user_name": "testuser",
                    "user_avatar": "/media/avatars/user2-avatar.png",
                    "text": "Hello",
                    "chat": 10,
                    "user": 2
                }
            ]
        }
        ```

-   Unsuccessful response:
    -   Status code: 500 (There is no chat with such ID).
    -   Response body:

        ```json
        {
            "type": "server_error",
            "errors": [
                {
                    "code": "error",
                    "detail": "Chat matching query does not exist.",
                    "attr": null
                }
            ]
        }
        ```

## Update message text
-   URL: https://prod-chat.duckdns.org/api/chat/message/<message_id>/
-   Request: Patch(URL, data)
    -   data: text

    ```
    URL = "https://prod-chat.duckdns.org/api/chat/message/5/"
    data = {"text": "Message text"}
    response = request.patch(URL, data)
    ```

-   Successful response:
    -   Status code: 200 Ok.
    -   Response body: Empty

        ```json
        {
            "id": 5,
            "user_name": "Nik",
            "user_avatar": "/media/avatars/avatar.jpg",
            "text": "Changed text",
            "timestamp": "2023-09-09T08:04:45.661872Z",
            "chat": 5,
            "user": 6
        }
        ```

-   Unsuccessful response:
    -   Status code: 405, 403, 404.
    -   Response body:

        ```json
        {
            "type": "client_error",
            "errors": [
                {
                    "code": "method_not_allowed",
                    "detail": "Method \"PUT\" not allowed.",
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
                    "code": "permission_denied",
                    "detail": "The action is allowed only to the author",
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
                    "code": "permission_denied",
                    "detail": "Only the message text can be changed",
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
                    "code": "not_found",
                    "detail": "Not found.",
                    "attr": null
                }
            ]
        }
        ```