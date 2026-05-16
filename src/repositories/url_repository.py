import os
from functools import cached_property


class UrlRepository:
    def __init__(self, table_name: str | None = None, dynamodb_resource=None):
        self.table_name = table_name or os.environ["DYNAMODB_TABLE"]
        self._dynamodb_resource = dynamodb_resource

    @cached_property
    def table(self):
        if self._dynamodb_resource:
            return self._dynamodb_resource.Table(self.table_name)

        import boto3

        return boto3.resource("dynamodb").Table(self.table_name)

    def save(self, record) -> None:
        self.table.put_item(Item=record.to_item())

    def find_by_code(self, code: str) -> dict | None:
        response = self.table.get_item(Key={"codigo": code})
        return response.get("Item")

    def exists(self, code: str) -> bool:
        return self.find_by_code(code) is not None
