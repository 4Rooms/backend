# Chat API


## Create chat
-   URL: https://prod-chat.duckdns.org/api/chat/
-   Request: Post(URL, data)  
    -   data: title, room, description (optional), img (optional)  
    -   chat titles cannot be repeated in the same room  
    -   __room__ must have one of the following string values:
        -   "films"
        -   "music"
        -   "books"
        -   "games"

    ```
    URL = "https://prod-chat.duckdns.org/api/chat/
    data = {"title": "Harry Potter",
            "room": "films",
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
                "creator": "userName",
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
    URL = "https://prod-chat.duckdns.org/api/chat/films/
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
                    "creator": "user1",
                    "description": "Who is your favorite character?",
                    "url": "/chat/films/1/",
                    "timestamp": "2023-08-04T20:12:10.777701Z"
                },
                {
                    "id": 2,
                    "title": "The Lord of the Rings films",
                    "room": "films",
                    "img": "https://prod-chat.duckdns.org/media/chat_img/frodo.jpg",
                    "creator": "user2",
                    "description": "Which film is the best in the series?",
                    "url": "/chat/films/2/",
                    "timestamp": "2023-08-04T20:14:30.256093Z"
                },
                {
                    "id": 3,
                    "title": "Friends",
                    "room": "films",
                    "img": "https://prod-chat.duckdns.org/media/chat_img/default.jpg",
                    "creator": "user1",
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
-   URL: https://prod-chat.duckdns.org/api/chat/<room>/<chatId>/
    -   __room__ must have one of the following string values:
        -   "films"
        -   "music"
        -   "books"
        -   "games"
-   Request: Patch(URL)
    -   data: description

    ```
    URL = "https://prod-chat.duckdns.org/api/chat/music/10/
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
            "creator": "Leslie",
            "description": "Chat description",
            "url": "/chat/music/10/",
            "timestamp": "2023-08-07T12:16:40.385811Z"
        }
        ```

-   Unsuccessful response:
    -   Status code: 400 Bad Request.
    -   Response body:

        ```json
        {
            "detail": "You do not have permission to perform this action."
        }
        ```

        ```json
        {
            "description": [
                "Ensure this field has no more than 400 characters."
            ]
        }
        ```