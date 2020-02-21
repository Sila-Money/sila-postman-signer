# Signer Server
VERY crude local proxy server to perform request signing with ECDSA and forward requests to desired host.

Designed as an API testing helper since most REST clients, like Postman, don't support signature authentication. Only designed for local use.

## How to use me
1. Clone me into a local directory. Change directory into my root (same directory as `manage.py` and `Makefile`).
2. From the terminal, run `make runserver`. By default, a local server will run on port 8181; you can specify a different port like `make runserver port=3001`.
3. Use me with the REST client of your choice. `/forward` is the endpoint that forwards requests onward.
4. If you want me to generate signature headers for you, set the Authorization header in requests to me like `Authorization: private-key; authsignature=[private key hex here]; usersignature=[private key hex here]`. To have me forward your request somewhere, set a header like `X-FORWARD-TO-URL: http://localhost:8000/0.2/check_handle`.
5. If you have any trouble with me, fix it yourself and push it up to help others using me! ;)
