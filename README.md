# Sila Signer Server + Postman Collection
Local proxy server served by Flask (https://flask.palletsprojects.com/en/1.1.x/) to perform request signing with ECDSA and forward requests to desired host.

Designed as an API testing helper since most REST clients, like Postman, don't support this signature authentication mechanism. Only designed for local use. **Do not serve this externally. When sending private keys in requests to this server, only set them in the Authorization header, which is not forwarded.**

Includes a Postman collection you can use to try out the [Sila sandbox API](https://docs.silamoney.com), but works with any REST client.

## Requirements
Make sure you have Python 3.6+. If on Mac or Linux, have bash and the ability to run make commands from a Makefile.

## Quickstart (Mac and Linux)
1. Clone me into a local directory. Change directory into my root (same directory as `Makefile`).
2. From the terminal, run `make venv`. This will install all dependencies into a local environment and only needs to be done once.
3. From the terminal, run `make runserver`. By default, a local server will run on port 8181; you can specify a different port like `make runserver port=3001`.
4. Use me with the REST client of your choice. `/forward` is the endpoint that signs requests and forwards them onward sans the original Authorization header. For convenience (not recommended for production use), you can generate new private key pairs with `/generate_private_key`, which also generates wallet verification signatures accepted by the Sila API when registering secondary wallets to users.
5. If you want me to generate signature headers for you, set the Authorization header in requests to me like `Authorization: private-key; [signature header name]=[private key hex here]; [another signature header name]=[private key hex here]`. To have me forward your request somewhere, set a header like `X-Forward-To-URL: http://sandbox.silamoney.com/0.2/check_handle`.
6. You can also set valid epoch timestamps and random UUID4 strings with the `X-Set-Epoch` and `X-Set-UUID` headers. You can specify which JSON key to set in the request like `X-Set-Epoch: header.created` or `X-Set-UUID: header.reference` (which each set keys in a nested dictionary like: `{"header": {"created": [sets epoch int in seconds]}}` and `{"header": {"reference": [sets random UUID4 string]}}`).
7. Open issues or contact support if you need more help. For security vulnerabilities, please email support@silamoney.com rather than opening a GitHub issue.

## Postman
This repository includes a Postman collection and a Postman environment. To use these, first have the Postman desktop application installed: https://www.postman.com/downloads/.

To import the collection, there should be an Import button in the top left corner of the Postman application. Click this and browse to the `Sila API v0.2 - Local Signer Server Edition.postman_collection.json` file in the postman folder of this repository.

To import the environment (which sets some defaults to make use of the collection easier), there should be a gear icon in the top right corner of the Postman application. When you click it, you should see an Import button. Click this and browse to the `SilaSandbox.postman_environment.json` file in the postman folder of this repository.

Before you start making requests through Postman, you'll want to set some of these environment variables. You can set them by selecting the Postman environment you imported in the upper-right dropdown, hitting the eye icon, and hitting the Edit button. Here is an explanation of each variable - you can add your own and edit the collection locally as well.

| Variable name | Default | Description |
| ------------- | :-----: | ----------- |
| `proxy_port` | 8181 | This is the localhost port where signerserver is expected to be running. If you started the signerserver on a different port, you will need to change this default value. |
| `host` | `https://sandbox.silamoney.com` | This is the host to which signed requests are forwarded. |
| `app_handle` | | This is the app handle you should have created in the [Sila console](https://console.silamoney.com). |
| `app_private_key` | | This is the ETH private key associated with the address registered with the given app handle on the console. |
| `user_handle` | | This is a user handle which you can check for availability and register with a user's verification data. This handle is always associated with at least one private key/address pair; this private key is not known to Sila. See [our docs](https://docs.silamoney.com) for more details. |
| `user_private_key` | | This is the ETH private key used to authenticate the user_handle. It must be associated with the public address that was registered with the user handle. |
| `user_address` | | This is the public ETH address sent in a /register request to register a user_handle. |
| `user_private_key2` | | This is a second private key that can be registered to a user handle and used in authentication. Make sure that a valid wallet verification signature is sent to register this key as a valid wallet. |
| `user_address2` | | Used when registering a second wallet address to a user. |
| `business_handle` | | A user handle that is registered as a business entity. |
| `business_private_key` | | ETH private key used to authenticate the business handle. |
| `business_address` | | Public ETH address registered with the business handle. |
