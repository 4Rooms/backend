# Chat API


## Post chat
-   URL: /api/chat/<room>/
-   Request: Post(URL, data)  
    -   data: title, description, img (optional)  
    -   chat titles cannot be repeated in the same room  
    -   __room__ must have one of the following string values:
        -   "films"
        -   "music"
        -   "books"
        -   "games"

    ```
    URL = "/api/chat/books/"
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
                "img": "/media/file.jpg",
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
                "Ensure this field has no more than 400 characters."
            ],
            "title": [
                "Ensure this field has no more than 70 characters."
            ]
        }
        ```

## Get chats from the certain room
-   URL: /api/chat/<room>/
    -   __room__ must have one of the following string values:
        -   "films"
        -   "music"
        -   "books"
        -   "games"
-   Request: Get(URL)

    ```
    URL = "/api/chat/films/"
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
                    "room": "films",
                    "img": "/media/chat_img/Hurry.jpg",
                    "user": "user1",
                    "description": "Who is your favorite character?",
                    "url": "/chat/films/1/",
                    "timestamp": "2023-08-04T20:12:10.777701Z"
                },
                {
                    "id": 2,
                    "title": "The Lord of the Rings films",
                    "room": "films",
                    "img": "/media/chat_img/frodo.jpg",
                    "user": "user2",
                    "description": "Which film is the best in the series?",
                    "url": "/chat/films/2/",
                    "timestamp": "2023-08-04T20:14:30.256093Z"
                },
                {
                    "id": 3,
                    "title": "Friends",
                    "room": "films",
                    "img": "/media/chat_img/default.jpg",
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

## Update chat description/img (Patch)
-   URL: /api/chat/<chatID>/
-   Request: Patch(URL, data)
    -   data: description/img or both fields

    ```
    URL = "/api/chat/10/"
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
                    "detail": "Ensure this field has no more than 400 characters.",
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

## Delete chat
-   URL: /api/chat/<chatID>/
-   Request: Delete(URL)

    ```
    URL = "/api/chat/10/"
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

## Get message history from the chat
-   URL: /api/chat/<chatID>/messages/
-   Request: Get(URL)

    ```
    URL = "/api/chat/10/messages/"
    response = request.get(URL)
    ```

-   Successful response:
    -   Status code: 200 OK.
    -   Response body: Empty

        ```json
        {
            "count": 2,
            "next": null,
            "previous": null,
            "results": [
                {
                    "id": 1,
                    "user_name": "user1",
                    "user_avatar": "/media/avatars/user1-avatar.jpg",
                    "text": "deleted",
                    "timestamp": "2023-09-12T14:28:35.244410Z",
                    "is_deleted": true,
                    "chat": 1,
                    "user": 1
                },
                {
                   "id": 2,
                    "user_name": "user2",
                    "user_avatar": "/media/avatars/user2-avatar.jpg",
                    "text": "Hello",
                    "timestamp": "2023-09-12T14:28:35.244410Z",
                    "is_deleted": false,
                    "chat": 1,
                    "user": 1
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
-   URL: /api/chat/message/<messageID>/
-   Request: Patch(URL, data)
    -   data: text

    ```
    URL = "/api/chat/message/5/"
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
            "is_deleted": false,
            "chat": 5,
            "user": 6
        }
        ```

-   Unsuccessful response:
    -   Status codes: 405, 403, 404.
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
        
        ```json
        {
           "type": "client_error",
            "errors": [
                {
                    "code": "permission_denied",
                    "detail": "The object was deleted",
                    "attr": null
                }
            ]
        }
        ```
        
## Delete message
-   URL: /api/chat/message/<messageID>/
-   Request: Delete(URL)

    ```
    URL = "/api/chat/message/10/"
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
        
        ```json
        {
           "type": "client_error",
            "errors": [
                {
                    "code": "permission_denied",
                    "detail": "The object was deleted",
                    "attr": null
                }
            ]
        }
        ```

-   Additional information:  
    When a message is deleted, it is stored in the database, it changed -> is_deleted=true, text=deleted.  
    When you call the get method to see the messages of a certain chat, all messages, including deleted ones, will be displayed.

## Get list of saved chats
-   URL: /api/chat/saved_chats/
-   Request: Get(URL)

    ```
    URL = "/api/chat/saved_chats/"
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
                    "url": "/chat/books/1/"
                },
                {
                    "id": 2,
                    "user": 7,
                    "chat": 10,
                    "title": "Imagine Dragons",
                    "room": "music",
                    "description": "Imagine Dragons Fans",
                    "chat_creator": "user2",
                    "img": "/media/chat_img3.jpg",
                    "url": "/chat/music/10/"
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
-   URL: /api/chat/saved_chats/
-   Request: Post(URL, data)

    ```
    URL = "/api/chat/saved_chats/"
    
    # the ID of the chat we want to save
    data = data = {"chat_id": chatId}
    
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
                "url": "/chat/music/10/"
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
-   URL: /api/chat/saved_chats/<savedChatID>/
-   Request: Post(URL)

    ```
    URL = "/api/chat/saved_chats/2/"
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
-   URL: /api/chat/my_chat/
-   Request: Get(URL)

    ```
    URL = "/api/chat/my_chat/"
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
                    "room": "films",
                    "img": ".../media/chat-img.jpg",
                    "user": "Carter",
                    "description": "Best character",
                    "url": "/chat/films/11/",
                    "timestamp": "2023-09-29T08:56:04.494009Z"
                },
                {
                    "id": 12,
                    "title": "The witcher",
                    "room": "games",
                    "img": ".../media/chat-avatar.jpg",
                    "user": "Carter",
                    "description": "How to pass",
                    "url": "/chat/games/12/",
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