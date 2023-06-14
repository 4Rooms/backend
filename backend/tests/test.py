import requests
import json

token = None

# login url
login_url = 'http://127.0.0.1:8000/api/auth/token/login/'
data = {'username': 'test',
        'password': 'W12345678'}

# logout url
logout_url = 'http://127.0.0.1:8000/api/auth/token/logout'

# headers for authentication
headers = None

# get users url
get_users_url = 'http://127.0.0.1:8000/api/users/'


def get_headers(token: str) -> dict:
    """Return headers for authorization"""

    return {'Authorization': f'token {token}'}


def login(login_url: str, data: dict) -> str:
    """Return token for authentication"""

    resp = requests.post(login_url, data=data)

    if resp.status_code == 200:
        auth_token = json.loads(resp.content)
        print(auth_token)
        token = auth_token.get('auth_token')
        return(token)
    else:
        print(f'Error {resp.status_code}: {resp.content}')
        return None


def logout(logout_url: str, data: dict, token: str) -> str:
    """Logout"""
    resp = requests.post(logout_url, data=data, headers=get_headers(token))
    print(resp.content)


def get_user_list(url: str, token: str):
    """Get user list"""

    resp = requests.get(url, headers=get_headers(token))
    if resp.status_code == 200:
        user_list = json.loads(resp.content)
        return user_list
    else:
        print(f'Error {resp.status_code}: {resp.content}')
        return None


# Login
token = login(login_url, data)
print('Token:', token)

if token:
    print('Headers:', get_headers(token))

    # Get user list
    users = get_user_list(get_users_url, token)
    for user in users:
        print(user, user)

# logout(logout_url, data=data, token=token)