# Chat API


## Post chat
-   URL: /api/chat/post/<room_name>/
-   Request: Post(URL, data)  
    -   data: title, description, img (optional)  
    -   chat titles cannot be repeated in the same room  
    -   __room__ must have one of the following string values:
        -   "cinema"
        -   "music"
        -   "books"
        -   "games"

    ```
    URL = "/api/chat/post/books/"
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
                "room": "books",
                "img": "/media/file.jpg",
                "user": "userName",
                "description": "Discussion of characters",
                "url": "/chat/books/3/",
                "likes": 0,
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
          "type": "client_error",
          "errors": [
            {
              "detail": "wrong room"
            }
          ]
        }
        ```

        ```json
        {
            "title": [
                "This field is required."
            ],
            "description": [
                "This field is required."
            ]
        }
        ```
        
        ```json
        {
            "title": [
                "This field may not be blank."
            ],
            "description": [
                "This field may not be blank."
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
                "Ensure this field has no more than 200 characters."
            ],
            "title": [
                "Ensure this field has no more than 50 characters."
            ]
        }
        ```

## Get chats from the certain room
-   URL: /api/chat/get/<room_name>/<sorting_name>/
    -   __room__ must have one of the following string values:
        -   "cinema"
        -   "music"
        -   "books"
        -   "games"
    -   __sorting_name__ must have one of the following string values:
        -   "new" - chat sorting from newest to oldest
        -   "old" - chat sorting from oldest to newest
        -   "popular" - chat sorting by the number of chat likes
-   Request: Get(URL)

    ```
    URL = "/api/chat/get/cinema/popular/"
    response = request.get(URL)
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
                    "room": "cinema",
                    "img": "/media/chat_img/Hurry.jpg",
                    "user": "user1",
                    "description": "Who is your favorite character?",
                    "url": "/chat/cinema/1/",
                    "likes": 5,
                    "timestamp": "2023-08-04T20:12:10.777701Z"
                },
                {
                    "id": 2,
                    "title": "The Lord of the Rings films",
                    "room": "cinema",
                    "img": "/media/chat_img/frodo.jpg",
                    "user": "user2",
                    "description": "Which film is the best in the series?",
                    "url": "/chat/cinema/2/",
                    "likes": 3,
                    "timestamp": "2023-08-04T20:14:30.256093Z"
                },
                {
                    "id": 3,
                    "title": "Friends",
                    "room": "cinema",
                    "img": "/media/chat_img/default.jpg",
                    "user": "user1",
                    "description": null,
                    "url": "/chat/cinema/3/",
                    "likes": 0,
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
          "type": "client_error",
          "errors": [
            {
              "detail": "wrong room"
            }
          ]
        }
        ```
        
        ```json
        {
          "type": "client_error",
          "errors": [
            {
              "detail": "wrong sorting_name"
            }
          ]
        }
        ```

## Update chat description/img (Patch)
-   URL: /api/chat/update/<chatID>/
-   Request: Patch(URL, data)
    -   data: description/img or both fields

    ```
    URL = "/api/chat/update/10/"
    data = {"description": "Chat description"}
    response = request.patch(URL, data)
    
    data = {"img": file.jpg}
    response = request.patch(URL, data)
    
    data = {"description": "Chat description", "img": file.jpg}
    response = request.patch(URL, data)
    ```

-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```json
        {
            "id": 10,
            "title": "Imagine Dragons",
            "room": "music",
            "img": "/media/chat_img/file.jpg",
            "user": "Leslie",
            "description": "Chat description",
            "url": "/chat/music/10/",
            "likes": 3,
            "timestamp": "2023-08-07T12:16:40.385811Z"
        }
        ```

-   Unsuccessful response:
    -   Status codes: 400 Bad Request, 403 Forbidden (user isn't a chat creator), 404 Not Found (Absent chat with posted ID).
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
            "type": "validation_error",
            "errors": [
                {
                    "code": "invalid_image",
                    "detail": "Upload a valid image. The file you uploaded was either not an image or a corrupted image.",
                    "attr": "img"
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
                    "detail": "Ensure this field has no more than 200 characters.",
                    "attr": "description"
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
                    "attr": "description"
                }
            ]
        }
        ```
        
        ```json
        {
            "img": [
                "Upload a valid image. The file you uploaded was either not an image or a corrupted image."
            ]
        }
        ```

## Delete chat (Now it's a WS Event)
-   URL: /api/chat/update/<chatID>/
-   Request: Delete(URL)

    ```
    URL = "/api/chat/update/10/"
    response = request.delete(URL)
    ```

-   Successful response:
    -   Status code: 204 No Content.
    -   Response body: Empty.
-   Unsuccessful response:
    -   Status codes: 404 Not Found (There is no chat with such ID), 403 Forbidden.
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

## Get list of saved chats
-   URL: /api/chat/saved_chats/get/<room>/
    -   __room__ must have one of the following string values:
        -   "cinema"
        -   "music"
        -   "books"
        -   "games"
-   Request: Get(URL)

    ```
    URL = "/api/chat/saved_chats/get/books/"
    response = request.get(URL)
    ```

-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```json
        {
            "count": 2,
            "next": null,
            "previous": null,
            "results": [
                {
                    "id": 1,
                    "user": 7,
                    "chat": 1,
                    "title": "Journey to the Center of the Earth",
                    "room": "books",
                    "description": "Jules Verne Fans",
                    "chat_creator": "user1",
                    "img": "/media/chat_avatar1.jpg",
                    "url": "/chat/books/1/",
                    "likes": 5
                },
                {
                    "id": 2,
                    "user": 7,
                    "chat": 10,
                    "title": "Patterns",
                    "room": "books",
                    "description": "Patterns",
                    "chat_creator": "user2",
                    "img": "/media/chat_img3.jpg",
                    "url": "/chat/books/10/",
                    "likes": 3
                }
            ]
        }
        ```
    -   user - ID of the user saving the chat
    -   chat_creator - username of the chat creator/owner
    -   img - URL of chat avatar
    -   url - URL as WebSocket chat
    -   count - number of all records in DB
    -   next - link to get the next 100 records by Get request on it
    -   previous - link to get the previous 100 records by Get request on it
    -   results - 100 or fewer records from DB (100 or fewer chats)
        
## Post saved chats
-   URL: /api/chat/saved_chats/post/
-   Request: Post(URL, data)

    ```
    URL = "/api/chat/saved_chats/post/"
    
    # the ID of the chat we want to save
    data = {"chat_id": chatId}
    
    response = request.post(URL, data)
    ```

-   Successful response:
    -   Status code: 201 Created.
    -   Response body:

        ```json
        {
            "saved_chat": {
                "id": 3,
                "user": 7,
                "chat": 10,
                "title": "Imagine Dragons",
                "room": "music",
                "description": "Imagine Dragons Fans",
                "chat_creator": "user2",
                "img": "/media/chat_img.jpg",
                "url": "/chat/music/10/",
                "likes": 3
            }
        }
        ```

-   Unsuccessful response:
    -   Status code: 500 (If the posted chat_id field doesn't exist. If the posted chai_id field is not a number or empty).
    -   Response body:

        ```json
        {   
            "type": "server_error",
            "errors": [
                {
                    "code": "error",
                    "detail": "'chat_id'",
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
                    "detail": "Field 'id' expected a number but got ''.",
                    "attr": null
                }
            ]
        }
        ```

## Delete saved chats
-   URL: /api/chat/saved_chats/delete/<savedChatID>/
-   Request: Post(URL)

    ```
    URL = "/api/chat/saved_chats/delete/2/"
    response = request.delete(URL)
    ```

-   Successful response:
    -   Status code: 204 No Content.
    -   Response body: Empty.
-   Unsuccessful response:
    -   Status code: 403 Forbidden (If the current user tries to delete another user's saved chat), 404 Not Found (Saved chat with posted ID doesn't exist)
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
                    "code": "not_found",
                    "detail": "Not found.",
                    "attr": null
                }
            ]
        }
        ```
        
## Get user-created chats (my chats)
-   URL: /api/chat/my_chats/get/<room>/
-   Request: Get(URL)
    -   __room__ must have one of the following string values:
        -   "cinema"
        -   "music"
        -   "books"
        -   "games"

    ```
    URL = "/api/chat/my_chat/get/cinema/"
    response = request.get(URL)
    ```

-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```json
        {
            "count": 2,
            "next": null,
            "previous": null,
            "results": [
                {
                    "id": 11,
                    "title": "The office",
                    "room": "cinema",
                    "img": ".../media/chat-img.jpg",
                    "user": "Carter",
                    "description": "Best character",
                    "url": "/chat/films/11/",
                    "likes": 5,
                    "timestamp": "2023-09-29T08:56:04.494009Z"
                },
                {
                    "id": 12,
                    "title": "The witcher",
                    "room": "cinema",
                    "img": ".../media/chat-avatar.jpg",
                    "user": "Carter",
                    "description": "How to pass",
                    "url": "/chat/cinema/12/",
                    "likes": 5,
                    "timestamp": "2023-09-29T09:10:36.637421Z"
                }
            ]
        }
        ```
    -   img - URL of chat avatar
    -   url - URL as WebSocket chat
    -   count - number of all records in DB
    -   next - link to get the next 100 records by Get request on it
    -   previous - link to get the previous 100 records by Get request on it
    -   results - 100 or fewer records from DB (100 or fewer chats)

-   Unsuccessful response:
    -   Status code: 400 Bad Request.
    -   Response body:

        ```json
        {
          "type": "client_error",
          "errors": [
            {
              "detail": "wrong room"
            }
          ]
        }
        ```

## Search chats 
-   URL: /api/chat/search/get/<room>/<phrase>/
-   Request: Get(URL)
    -   __room__ must have one of the following string values:
        -   "cinema"
        -   "music"
        -   "books"
        -   "games"
    -   __phrase__ - phrase or word by which we search for a chat

    ```
    URL = "/api/chat/search/get/games/witcher/"
    response = request.get(URL)
    ```

-   Successful response:
    -   Status code: 200.
    -   Response body:

        ```json
        {
            "count": 2,
            "next": null,
            "previous": null,
            "results": [
                {
                   "id": 19,
                   "title": "The witcher 3",
                   "room": "games",
                   "img": ".../media/vatar.jpg",
                   "user": "Terry",
                   "description": "How to pass",
                   "url": "/chat/games/19/",
                   "timestamp": "2023-10-06T08:39:16.155425Z",
                   "likes": 0
                },
                {
                    "id": 17,
                    "title": "The witcher 2",
                    "room": "games",
                    "img": ".../media/avatar.jpg",
                    "user": "Mary",
                    "description": "How to pass",
                    "url": "/chat/games/17/",
                    "timestamp": "2023-10-06T08:16:46.221209Z",
                    "likes": 1
                }
            ]
        }
        ```
    -   img - URL of chat avatar
    -   url - URL as WebSocket chat
    -   count - number of all records in DB
    -   next - link to get the next 100 records by Get request on it
    -   previous - link to get the previous 100 records by Get request on it
    -   results - 100 or fewer records from DB (100 or fewer chats)

-   Unsuccessful response:
    -   Status code: 400 Bad Request.
    -   Response body:

        ```json
        {
          "type": "client_error",
          "errors": [
            {
              "detail": "wrong room"
            }
          ]
        }
        ```