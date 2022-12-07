from root.celery import app
import requests
import json
from requests.exceptions import ConnectionError
from urllib3.exceptions import NewConnectionError
from celery import Task

from datetime import datetime, timezone


def update_message_status_to_request_error(msg):
    msg.status = "request_error"
    msg.save()


def update_message_status_to_failed(msg):
    msg.status = "lost connection with server"
    msg.save()


def update_message_sending_start(msg):
    msg.creating_date = datetime.now(timezone.utc)
    msg.save()


def update_message_status_to_success(msg):
    msg.status = "success"
    msg.save()


def update_message_status_to_expired(msg):
    msg.status = "expired"
    msg.save()


def make_request(msg):
    url = f"https://probe.fbrq.cloud/v1/send/{msg.id}"
    token = (
        "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        ".eyJleHAiOjE3MDEzNDc2MDksImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6ImFydHNpb21fcGgifQ"
        ".G9fA5XoHOKIAHz8V4FSgVmEgkyf38IpqvBJsFZ90LJo "
    )
    data = json.dumps(
        {
            "id": msg.id,
            "phone": msg.client.tel_number,
            "text": msg.distribution.message_text,
        }
    )

    response = requests.post(
        url=url,
        data=data,
        headers={"Content-Type": "application/json", "Authorization": token},
    )
    return response


@app.task(
    bind=True,
    autoretry_for=(ConnectionError, NewConnectionError),
    retry_backoff=True,
    retry_kwargs={"max_retries": 7},
    default_retry_delay=5 * 60
)
def send_message(self: Task, message, expires):
    update_message_sending_start(message)

    if expires > datetime.now(timezone.utc):

        response = make_request(message)

        if response.status_code == 200:
            update_message_status_to_success(message)
        if response.status_code == 400:
            update_message_status_to_request_error(message)

    else:
        update_message_status_to_expired(message)
        self.app.control.revoke(self.request.id, terminate=True)


@app.task
def error_handling(request, exc, traceback, *args):
    update_message_status_to_failed(args[0])
