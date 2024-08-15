from datetime import date, datetime
from decimal import Decimal
from typing import Any

from interfaces import Service
from simplejson import dumps, loads


class JsonSerializer(Service):
    def __init__(self, date_format: str) -> None:
        self.date_format = date_format

    def serialize(self, object_: Any):
        if isinstance(object_, date):
            return object_.strftime(self.date_format)
        else:
            return object_

    def json_dump(self, object_, **kwargs):
        return dumps(object_, default=self.serialize, use_decimal=True, **kwargs)

    def __call__(self, object_, **kwargs):
        return self.json_dump(object_, **kwargs)


class JsonDeserializer(Service):
    def __init__(self, date_format: str) -> None:
        self.date_format = date_format

    def deserialize_date(self, json_dict: dict | list):
        def _parse_date(value: str):
            """
            Парсим только даты, потому что записываем мы тоже даты. По-хорошему надо записывать в формат дата-время
            """
            try:
                new_value = datetime.strptime(value, self.date_format).date()
            except (TypeError, ValueError):
                return value
            return new_value

        for key, value in json_dict.items():
            if isinstance(value, list):
                for i, item in enumerate(value):
                    value[i] = _parse_date(item)
            else:
                json_dict[key] = _parse_date(value)

        return json_dict

    def json_load(self, json, **kwargs):
        return loads(json, object_hook=self.deserialize_date, use_decimal=Decimal, **kwargs)

    def __call__(self, json, **kwargs):
        return self.json_load(json, **kwargs)
