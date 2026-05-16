import json
from http import HTTPStatus

from services.shortener_service import ShortenerService


def route(event):
    method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")

    if method == "POST":
        return ShortenerService().shorten(event)

    if method == "OPTIONS":
        return {
            "statusCode": HTTPStatus.NO_CONTENT,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
            },
        }

    return {
        "statusCode": HTTPStatus.METHOD_NOT_ALLOWED,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({"message": "Method not allowed"}),
    }
