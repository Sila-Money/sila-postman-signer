FROM python:3.9.13-buster

LABEL Author="SilaMoney"
LABEL Version="1.1.0"


WORKDIR /signer-server
ADD . /signer-server
RUN pip install -r requirements.txt

EXPOSE 8181

ENV PYTHONDONTWRITEBYTECODE 1
ENV FLASK_APP signerserver/application.py
ENV FLASK_ENV production
CMD ["flask", "run", "--port=8181", "--host=0.0.0.0"]
