# WebSocket Events

## Chat Events

### Event chat_message
If the client has sent the message to chat, the server expects 
to receive the following structure from the client:

```json
{
 "event_type": "chat_message",
  "message": {
    "chat": 39,
    "text": "Hi"
  }
}
```
-   "id": message ID

If the message passes validation the event with the following structure is sent to a group of users in the chat:

```json
{
  "event_type": "chat_message",
  "message": {
    "id": 40,
    "user_name": "user3",
    "user_avatar": "/media/default-user-avatar.jpg",
    "text": "Message text",
    "timestamp": "2023-09-26T14:17:44.250236Z",
    "is_deleted": false,
    "chat": 1,
    "user": 3,
  },
  "timestamp": "2023-09-26T14:17:44.250236Z"
}
```

### Event connected_user (the user joined to chat)
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

### Event disconnected_user (the user left the chat)
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

### Event online_user_list (list of users connected to a current chat)
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

### Event message_was_deleted
If the client has deleted his message from the chat, the server expects 
to receive the following structure from the client:

```json
{
  "event_type": "message_was_deleted", 
  "id": 86
}
```
-   "id" - Message ID

If there is a message with the specified ID in DB and the user from the request 
is the author of the message, the text of the message will be changed to "deleted". 
The server will send the following structure to a group of users in the chat:

```json
{
  "event_type": "message_was_deleted", 
  "id": 86,
  "timestamp": "2023-09-26T14:17:44.250236Z"
}
```

### Event message_was_updated
If the client has changed the message text, 
the server expects the following structure from the client:

```json
{
  "event_type": "message_was_updated",
  "id": 10,
  "new_text": "New Text" 
}
```
-   "id" - Message ID

If the updated text is valid, there is a message with the specified ID, 
this message has not been deleted before, and the user from the request 
is the author of the message, the server will send the following structure 
to the chat group:

```json
{
  "event_type": "message_was_updated",
  "id": 10,
  "new_text": "New Text",
  "timestamp": "2023-09-26T14:17:44.250236Z"
}
```

### Event chat_was_deleted
If a client has deleted his chat, the server expects 
to receive the following structure from the client:

```json
{
  "event_type": "chat_was_deleted"
}
```

If the user from the request is the author of the chat, the chat will be deleted. 
The server will send the following structure to a group of users in the chat:

```json
{
  "event_type": "chat_was_deleted", 
  "id": 34,
  "timestamp": "2023-09-26T14:17:44.250236Z"
}
```
-   "id": chat ID

### Event chat_was_liked/unliked
If a client has liked/unliked the chat, the server expects 
to receive the following structure from the client:

```json
{
  "event_type": "chat_was_liked/unliked"
}
```
 
The server will save like in DB and send the following structure to a group of users 
in the chat if there is no record in the DB that this user liked the chat:

```json
{
  "event_type": "chat_was_liked", 
  "id": 34,
  "user": "Terry",
  "timestamp": "2023-09-26T14:17:44.250236Z"
}
```
-   "id": chat ID

The server will delete like and send the following structure to a group of users 
in the chat if the user has already liked the current chat:

```json
{
  "event_type": "chat_was_unliked", 
  "id": 34,
  "user": "Terry",
  "timestamp": "2023-09-26T14:17:44.250236Z"
}
```

### Event message_reaction
If a client has reacted the message, the server expects 
to receive the following structure from the client:

```json
{
  "event_type": "message_reaction", 
  "id": 35,
  "reaction": "👍"
}
```
 
The server will save reaction in DB and send the following structure to a group of users 
in the chat if there wasn't record in the DB that this user reacted to that message with a posted emoji:

```json
{
  "event_type": "message_reaction_was_posted",
  "id": 35,
  "reaction": "👍",
  "user": "Terry",
  "timestamp": "2023-09-26T14:17:44.250236Z"
}
```
-   "id": message ID

The server will delete posted reaction and send the following structure to a group of users 
in the chat if the user has already reacted to that message with a posted emoji:

```json
{
  "event_type": "message_reaction_was_deleted",
  "id": 131,
  "reaction": "👍",
  "user": "Terry",
  "timestamp": "2023-09-26T14:17:44.250236Z"
}
```

## Error Event

If the server could not process any websocket message received from a user, the server will
reply with `error` event type:

```json
{
  "event_type": "error",
  "error_message": "Error message",
  "details": {
    "user_id": 0,
    "user_name": "username",
    "chat_id": 0,
    "message_id": 0
  }
}
```
