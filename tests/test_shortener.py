import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from services.shortener_service import ShortenerService


EXAMPLE_ORIGINAL_URL = "https://youtu.be/xFrGuyw1V8s?si=Biwdg-LYqohj05Px"


def build_event(url: str, method: str = "POST") -> dict:
    return {
        "httpMethod": method,
        "body": json.dumps({"url": url}),
    }


def parse_body(response: dict) -> dict:
    return json.loads(response["body"])


class ShortenerServiceTest(unittest.TestCase):
    def test_valid_url_returns_short_url_and_saves_record(self):
        repository = MagicMock()
        repository.exists.return_value = False

        with patch("services.shortener_service.secrets.choice", side_effect=list("abc123")):
            service = ShortenerService(repository=repository, base_url="https://sho.rt")
            response = service.shorten(build_event(EXAMPLE_ORIGINAL_URL))

        body = parse_body(response)

        self.assertEqual(response["statusCode"], 201)
        self.assertEqual(body["code"], "abc123")
        self.assertEqual(body["short_url"], "https://sho.rt/abc123")
        self.assertEqual(body["url_original"], EXAMPLE_ORIGINAL_URL)
        repository.save.assert_called_once()

        saved_record = repository.save.call_args.args[0]
        self.assertEqual(saved_record.codigo, "abc123")
        self.assertEqual(saved_record.url_original, EXAMPLE_ORIGINAL_URL)
        self.assertEqual(saved_record.clicks, 0)

    def test_invalid_url_returns_bad_request_and_does_not_save(self):
        repository = MagicMock()
        service = ShortenerService(repository=repository, base_url="https://sho.rt")

        response = service.shorten(build_event("not-a-url"))

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(parse_body(response)["message"], "Invalid URL. Provide a valid http or https URL.")
        repository.exists.assert_not_called()
        repository.save.assert_not_called()

    def test_code_collision_retries_until_unique_code(self):
        repository = MagicMock()
        repository.exists.side_effect = [True, False]

        choices = list("ABC123XYZ789")
        with patch("services.shortener_service.secrets.choice", side_effect=choices):
            service = ShortenerService(repository=repository, base_url="https://sho.rt")
            response = service.shorten(build_event(EXAMPLE_ORIGINAL_URL))

        body = parse_body(response)

        self.assertEqual(response["statusCode"], 201)
        self.assertEqual(body["code"], "XYZ789")
        self.assertEqual(repository.exists.call_count, 2)
        repository.save.assert_called_once()
        self.assertEqual(repository.save.call_args.args[0].codigo, "XYZ789")

    def test_repository_uses_boto3_table_for_get_and_put(self):
        from models.url_model import UrlRecord
        from repositories.url_repository import UrlRepository

        table = MagicMock()
        table.get_item.return_value = {"Item": {"codigo": "abc123"}}
        dynamodb = MagicMock()
        dynamodb.Table.return_value = table

        repository = UrlRepository(table_name="urls", dynamodb_resource=dynamodb)
        record = UrlRecord(
            codigo="abc123",
            url_original=EXAMPLE_ORIGINAL_URL,
            created_at="2026-05-16T00:00:00+00:00",
        )

        repository.save(record)
        item = repository.find_by_code("abc123")

        dynamodb.Table.assert_called_once_with("urls")
        table.put_item.assert_called_once_with(Item=record.to_item())
        table.get_item.assert_called_once_with(Key={"codigo": "abc123"})
        self.assertEqual(item, {"codigo": "abc123"})

    def test_service_can_read_required_values_from_environment(self):
        repository = MagicMock()
        repository.exists.return_value = False

        with patch.dict(os.environ, {"BASE_URL": "https://env.example"}, clear=False):
            with patch("services.shortener_service.secrets.choice", side_effect=list("env001")):
                service = ShortenerService(repository=repository)
                response = service.shorten(build_event(EXAMPLE_ORIGINAL_URL))

        self.assertEqual(parse_body(response)["short_url"], "https://env.example/env001")


if __name__ == "__main__":
    unittest.main()
