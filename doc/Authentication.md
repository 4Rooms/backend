### Authorization using a token.
Advantages of tokens over cookies:
1.  Authorization of those clients who simply don't have a cookie mechanism (that is, users do not log in through a web browser);
2.  Tokens do not need CSRF protection, because they are not automatically issued by the client for each request, as is the case with cookies.

### Authentication algorithm
#### The token is received when logging in
![img_1.png](img/img_1.png)

To authenticate clients, the token key must be included in the Authorization HTTP header. The key must be prefixed with the string literal "Token", with spaces separating the two strings.  
For example:

Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

```python
token = '9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b'
headers = {'Authorization': 'Token ' + token}
```

#### Using tokenized requests

![img.png](img/img.png)

### Requests
#### Login

```python
data = {'username': 'test',
        'password': 'W12345678'} 
```

Method: Post (URL, data=data)  
URL: http://olalab.hopto.org:8888/api/auth/token/login/

-   If a user exists in DB, you get a response with a token, which you should save for other requests for that user.  
    Example of a response with a token: `{'auth_token': '5719d2a8680f6848f5ce9e36bea59b6783c3f04a'}`
-   If the user doesn't exist in DB, you get Error 401.

#### Logout

```python
token = '9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b'
data = {'username': 'test',
        'password': 'W12345678'}
headers={'Authorization': 'Token ' + token}
```

Method: Post (URL, data=data, headers=headers)  
URL: http://olalab.hopto.org:8888/api/auth/token/logout/
