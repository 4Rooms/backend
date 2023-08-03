# Chat API


## Create chat
-   URL: https://prod-chat.duckdns.org/api/create-chat/
-   Request: Post(URL, data)  
    data: title, room, description (optional), img (optional)  
    __room__ must have one of the following string values:
    -   "films"
    -   "music"
    -   "books"
    -   "games"

    ```
    URL = "https://prod-chat.duckdns.org/api/create-chat/"
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
                "timestamp": "2023-08-03T08:51:26.593514Z",
                "url": "/chat/Harry Potter/42/films/"
            }
        }
        ```

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