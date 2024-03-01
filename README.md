# Sila Signer Server + Postman Collection
Lightweight local proxy server served by Flask (https://flask.palletsprojects.com/en/1.1.x/) to perform request signing with ECDSA and forward requests to desired host.

Designed as an API testing helper since most REST clients, like Postman, don't support this signature authentication mechanism. Only designed for local use. **Do not serve this externally. When sending private keys in requests to this server, only set them in the Authorization header, which is not forwarded.**

Includes a Postman collection you can use to try out the [Sila sandbox API](https://docs.silamoney.com), but works with any REST client.

## Requirements
Either:
* [Docker](https://docs.docker.com/get-docker/) is installed.  (see: [Running in a Docker container](#run-the-signer-server-in-a-docker-container))

or: (see: [Building and running from source](#building-and-running-the-signer-server-from-source))
* Python 3.12.2
* python [venv](https://docs.python.org/3.9.13/library/venv.html) module (seems to not ship with Ubuntu)
* bash
* the ability to run `make` commands from a Makefile.

## Quickstart (Mac and Linux)
**NOTE**: the signer-server default port is **8181**

### Run the signer-server in a Docker container
This option eliminates the requirement for a Python 3.12.2 installation.

You'll need [Docker](https://docs.docker.com/get-docker/) installed in order to build and run Docker images and containers.
1. Build the Docker image (should only need to be done once): 
   * with `make`: `make docker-image`
   * without `make`: `docker build -t sila-signer-server .`
1. Start the Docker container and access the server at the **default port 8181**:
   * with `make`: `make docker-run`
   * without `make`: `docker run -p 8181:8181 sila-signer-server`

##### Specifying a non-default port for the Docker container
Make the signer-server accessible on (for example) port 3001 of the container:
 
`docker run -p 3001:8181 sila-signer-server`
### Building and running the signer-server from source
1. Have a copy of **Python 3.12.2** installed; later versions of Python may be supported, but are untested.  We recommend [pyenv](https://github.com/pyenv/pyenv) for managing multiple Python versions. 
1. Clone me into a local directory. Change directory into my root (same directory as `Makefile`).
1. From the terminal, run `make venv`. This will install all dependencies into a local environment and only needs to be done once.
1. From the terminal, run `make runserver`
##### Specifying a non-default port
You can specify that the server run on a different port wth:
 
`make runserver port=3001`.


### Routing requests through the signer server
1. Use me with the REST client of your choice. `/forward` is the endpoint that signs requests and forwards them onward sans the original Authorization header. For convenience (not recommended for production use), you can generate new private key pairs with `/generate_private_key`, which also generates wallet verification signatures accepted by the Sila API when registering secondary wallets to users.
1. If you want me to generate signature headers for you, set the Authorization header in requests to me like `Authorization: private-key; [signature header name]=[private key hex here]; [another signature header name]=[private key hex here]`. To have me forward your request somewhere, set a header like `X-Forward-To-URL: http://sandbox.silamoney.com/0.2/check_handle`.
1. You can also set valid epoch timestamps and random UUID4 strings with the `X-Set-Epoch` and `X-Set-UUID` headers. You can specify which JSON key to set in the request like `X-Set-Epoch: header.created` or `X-Set-UUID: header.reference` (which each set keys in a nested dictionary like: `{"header": {"created": [sets epoch int in seconds]}}` and `{"header": {"reference": [sets random UUID4 string]}}`).
1. Open issues or contact support if you need more help. For security vulnerabilities, please email support@silamoney.com rather than opening a GitHub issue.

## Postman
This repository includes a Postman collection and a Postman environment. To use these, first have the Postman desktop application installed: https://www.postman.com/downloads/. **Make sure your local installation is up to date!** One known issue with importing this collection into older versions of Postman is that you may not have the Authorization API key option and will have to manually set the Authorization header on all requests (which is a pain, but you should still be able to use this collection).

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
