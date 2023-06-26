# Accounts App Documentation

## User registration
![img.png](img/register.png)
-  URL: https://prod-chat.duckdns.org/api/register/
-  Request: Post(URL, {email, password}).  
   Request doesn't require any token in headers.
   ```
   URL = "https://prod-chat.duckdns.org/api/register/"
   data = {"email": "user@gmail.com",
           "password": "UserPassword"}
   response = request.post(URL, data)
   ```
-  Successful response:
   -  Status code: 201.
   -  Response body:
   ```
   {
       "id": 2,
       "email": "user@gmail.com",
       "is_email_confirmed": false
   } 
   ```
-  Additional information:  
   In case of a response with a status code of 201, the user will be sent a link to confirm his email. If the user follows the link, the value of the variable is_email_confirm will change to True.
## Authorization using a JWT (JSON Web Token).
## Login
![img_1.png](img/login.png)
-  URL: https://prod-chat.duckdns.org/api/token/
-  Request: Post(URL, {email, password}).  
   Request doesn't require any token in headers.
   ```
   URL = "https://prod-chat.duckdns.org/api/token/"
   data = {"email": "user@gmail.com",
           "password": "UserPassword"}
   response = request.post(URL, data)
   ```
-  Successful response:
   -  Status code: 200.
   -  Response body:
   ```
   {
       "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4ODIxMTEzMiwiaWF0IjoxNjg3MzQ3MTMyLCJqdGkiOiIxMDBkODBlYzgzNTg0ZGI1YmExODQ5Njc3ODg0OWNjYSIsInVzZXJfaWQiOjEzfQ.aL849Cdf-s8htmOjimA9fqQ643in3K7kO_YeNbNzGmM",
       "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg3NDMzNTMyLCJpYXQiOjE2ODczNDcxMzIsImp0aSI6Ijk4MGM3MjU4ZTNmMDQ4NmViZmU3OTMxYzBkMmQzMGIzIiwidXNlcl9pZCI6MTN9.wwT_HBIP_e9gUFLIL7emd4H8xf75GM8jKskdihnRlu4"
   }
   ```
-  Additional information: 
   We should save JWT because to authenticate the user in requests that require authentication, the access token key must be included in the Authorization HTTP header. The access token must be prefixed with the string literal "Bearer", with spaces separating the two strings.
   ```
   access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg3NDMzNTMyLCJpYXQiOjE2ODczNDcxMzIsImp0aSI6Ijk4MGM3MjU4ZTNmMDQ4NmViZmU3OTMxYzBkMmQzMGIzIiwidXNlcl9pZCI6MTN9.wwT_HBIP_e9gUFLIL7emd4H8xf75GM8jKskdihnRlu4"
   headers = {"Authorization": "Bearer " + access_token}
   ```
-  The access token expires after 1 day.
-  We can easily persist users between refreshes and login without any credentials. Whenever a token expires or a user refreshes we can get a new access token by sending a request to refresh token.
## Refresh token
![img_1.png](img/refresh.png)
-  URL: https://prod-chat.duckdns.org/api/token/refresh/
-  Request: Post({"refresh": "eyJhbGciOiJ..."}).  
   Request doesn't require any token in headers. Request requires refresh token in data.
   ```
   URL = "https://prod-chat.duckdns.org/api/token/refresh/"
   data = {"refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4ODIxMTEzMiwiaWF0IjoxNjg3MzQ3MTMyLCJqdGkiOiIxMDBkODBlYzgzNTg0ZGI1YmExODQ5Njc3ODg0OWNjYSIsInVzZXJfaWQiOjEzfQ.aL849Cdf-s8htmOjimA9fqQ643in3K7kO_YeNbNzGmM"}
   response = request.post(URL, data)
   ```
-  Successful response:
   -  Status code: 200.
   -  Response body:
   ```
   {
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg3NDM1OTU0LCJpYXQiOjE2ODczNDcxMzIsImp0aSI6IjkwM2FhNmRhNjhjZDQxZGY4ZjNhODYzNGY5MzhkNzc3IiwidXNlcl9pZCI6MTN9.TDFu-WU9shZr0VvpGOkGadMysavc5nKxDxR8ASxeaWs"
   }
   ```

## Get the current user info
![img.png](img/get_data.png)
- URL: https://prod-chat.duckdns.org/api/user/
-  Request: Get(URL, headers={"Authorization": 'Bearer ' + access_token}).  
   Request requires access token in headers.
  ```
  access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg3NDM1OTU0LCJpYXQiOjE2ODczNDcxMzIsImp0aSI6IjkwM2FhNmRhNjhjZDQxZGY4ZjNhODYzNGY5MzhkNzc3IiwidXNlcl9pZCI6MTN9.TDFu-WU9shZr0VvpGOkGadMysavc5nKxDxR8ASxeaWs"
  headers = {"Authorization": "Bearer " + access_token}
  response = request.get(URL, headers)
  ```
-  Successful response:
   -  Status code: 200.
   -  Response body:
  ```
  {
      "id": 5,
      "email": "user@gmail.com",
      "is_email_confirmed": false/true
  }
  ```
