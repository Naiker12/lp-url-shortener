import base64
import json
import os
import re
import secrets
import string
from datetime import UTC, datetime
from http import HTTPStatus

from models.url_model import UrlRecord
from repositories.url_repository import UrlRepository


URL_REGEX = re.compile(
    r"^(?:https?):\/\/"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,63}"
    r"(?::\d{2,5})?"
    r"(?:[\/?#][^\s]*)?$"
)

CODE_ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6
MAX_GENERATION_ATTEMPTS = 10


class ShortenerService:
    def __init__(
        self,
        repository: UrlRepository | None = None,
        base_url: str | None = None,
        code_length: int = CODE_LENGTH,
    ):
        self.repository = repository or UrlRepository()
        self.base_url = (base_url or os.environ["BASE_URL"]).rstrip("/")
        self.code_length = code_length

    def shorten(self, event) -> dict:
        body = self._parse_body(event)
        original_url = body.get("url")

        if not self._is_valid_url(original_url):
            return self._response(
                HTTPStatus.BAD_REQUEST,
                {"message": "Invalid URL. Provide a valid http or https URL."},
            )

        code = self._generate_unique_code()
        record = UrlRecord(
            codigo=code,
            url_original=original_url,
            created_at=datetime.now(UTC).isoformat(),
        )
        self.repository.save(record)

        return self._response(
            HTTPStatus.CREATED,
            {
                "code": code,
                "short_url": f"{self.base_url}/{code}",
                "url_original": original_url,
            },
        )

    def _generate_unique_code(self) -> str:
        for _ in range(MAX_GENERATION_ATTEMPTS):
            code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(self.code_length))
            if not self.repository.exists(code):
                return code

        raise RuntimeError("Could not generate a unique code")

    @staticmethod
    def _parse_body(event) -> dict:
        raw_body = event.get("body") or "{}"

        if event.get("isBase64Encoded"):
            raw_body = base64.b64decode(raw_body).decode("utf-8")

        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError:
            return {}

        return body if isinstance(body, dict) else {}

    @staticmethod
    def _is_valid_url(url: str | None) -> bool:
        return isinstance(url, str) and URL_REGEX.match(url) is not None

    @staticmethod
    def _response(status_code: HTTPStatus, payload: dict) -> dict:
        return {
            "statusCode": status_code,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(payload),
        }
