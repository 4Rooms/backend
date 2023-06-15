import requests


def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.
    """
    print(
        "{}\n{}\r\n{}\r\n\r\n{}".format(
            "-----------START-----------",
            req.method + " " + req.url,
            "\r\n".join("{}: {}".format(k, v) for k, v in req.headers.items()),
            req.body,
        )
    )


# Get token
get_token_url = "http://127.0.0.1:8000/api/token/"
data = {"username": "ola", "password": "samsung1234"}


# req = requests.Request('POST', get_token_url, data=data)
# prepared = req.prepare()
# pretty_print_POST(prepared)


resp = requests.post(get_token_url, json=data)

# pretty_print_POST(prepared)

tokens = resp.json()
print(tokens)

# Test get request
get_users_url = "http://127.0.0.1:8000/api/users/"
headers = {"Authorization": f'Bearer {tokens.get("access")}'}
print(headers)

resp = requests.get(get_users_url, headers=headers)

print(resp.json())
