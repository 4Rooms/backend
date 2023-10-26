# Message API


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

## Update message text (Now it is WebSocket Event)
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
        
## Delete message (Now it is WebSocket Event)
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