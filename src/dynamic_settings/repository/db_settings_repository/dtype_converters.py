from datetime import datetime, timedelta
from typing import Any


class DTypeConverter:
    PYTHON_TYPE: type
    TYPE_NAME: str

    def to_db_format(self, value: Any) -> str:
        raise NotImplementedError

    @staticmethod
    def to_python_type(self, value: str) -> Any:
        raise NotImplementedError


class IntDTypeConverter(DTypeConverter):
    PYTHON_TYPE = int
    TYPE_NAME = "integer"

    def to_db_format(self, value: int) -> str:
        return str(value)

    def to_python_type(self, value: str) -> int:
        return int(value)


class FloatDTypeConverter(DTypeConverter):
    PYTHON_TYPE = float
    TYPE_NAME = "float"

    def to_db_format(self, value: float) -> str:
        return str(value)

    def to_python_type(self, value: str) -> float:
        return float(value)


class StrDTypeConverter(DTypeConverter):
    PYTHON_TYPE = str
    TYPE_NAME = "string"

    def to_db_format(self, value: str) -> str:
        return value

    def to_python_type(self, value: str) -> str:
        return value


class NoneDTypeConverter(DTypeConverter):
    PYTHON_TYPE = type(None)
    TYPE_NAME = "none"

    def to_db_format(self, value: Any) -> str:
        return ""

    def to_python_type(self, value: str) -> None:
        return None


class BooleanDTypeConverter(DTypeConverter):
    PYTHON_TYPE = bool
    TYPE_NAME = "boolean"

    def to_db_format(self, value: bool) -> str:
        return str(value)

    def to_python_type(self, value: str) -> bool:
        if value == "True":
            converted_value = True
        else:
            converted_value = False
        return converted_value


class DatetimeDTypeConverter(DTypeConverter):
    PYTHON_TYPE = datetime
    TYPE_NAME = "datetime"

    def to_db_format(self, value: datetime) -> str:
        return value.isoformat()

    def to_python_type(self, value: str) -> datetime:
        return datetime.fromisoformat(value)


class TimedeltaDTypeConverter(DTypeConverter):
    PYTHON_TYPE = timedelta
    TYPE_NAME = "timedelta"

    def to_db_format(self, value: timedelta) -> str:
        return str(value.total_seconds())

    def to_python_type(self, value: str) -> timedelta:
        return timedelta(seconds=float(value))
