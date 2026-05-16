import json
from http import HTTPStatus

from services.shortener_service import ShortenerService


def route(event):
    method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")

    if method == "POST":
        return ShortenerService().shorten(event)

    return {
        "statusCode": HTTPStatus.METHOD_NOT_ALLOWED,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Method not allowed"}),
    }
