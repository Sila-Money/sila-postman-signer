# Signer Server
Local proxy server served by Flask (https://flask.palletsprojects.com/en/1.1.x/) to perform request signing with ECDSA and forward requests to desired host.

Designed as an API testing helper since most REST clients, like Postman, don't support this signature authentication mechanism. Only designed for local use.

Includes a Postman collection you can use to try out the Sila sandbox API.

## Quickstart
1. Clone me into a local directory. Change directory into my root (same directory as `Makefile`).
2. From the terminal, run `make venv`. This will install all dependencies are installed into a local environment.
3. From the terminal, run `make runserver`. By default, a local server will run on port 8181; you can specify a different port like `make runserver port=3001`.
4. Use me with the REST client of your choice. `/forward` is the endpoint that signs requests and forwards them onward sans the original Authorization header.
5. If you want me to generate signature headers for you, set the Authorization header in requests to me like `Authorization: private-key; authsignature=[private key hex here]; usersignature=[private key hex here]`. To have me forward your request somewhere, set a header like `X-Forward-To-URL: http://sandbox.silamoney.com/0.2/check_handle`.
6. You can also set valid epoch timestamps and random UUID4 strings with the `X-Set-Epoch` and `X-Set-UUID` headers. You can specify which JSON key to set in the request like `X-Set-Epoch: header.created` or `X-Set-UUID: header.reference` (which set keys in a nested dictionary like: `{"header": {"created": [sets epoch int in seconds]}}` and `{"header": {"reference": [sets random UUID4 string]}}`).
7. Open issues or contact support if you need more help. For security vulnerabilities, please email support@silamoney.com rather than opening a GitHub issue.
