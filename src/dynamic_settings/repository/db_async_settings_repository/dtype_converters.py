from datetime import datetime, timedelta
from typing import Any


class DTypeConverter:
    PYTHON_TYPE: type
    TYPE_NAME: str

    @staticmethod
    def to_db_format(value: Any) -> str:
        raise NotImplementedError

    @staticmethod
    def to_python_type(value: str) -> Any:
        raise NotImplementedError


class IntDTypeConverter(DTypeConverter):
    PYTHON_TYPE = int
    TYPE_NAME = "integer"

    @staticmethod
    def to_db_format(value: int) -> str:
        return str(value)

    @staticmethod
    def to_python_type(value: str) -> int:
        return int(value)


class FloatDTypeConverter(DTypeConverter):
    PYTHON_TYPE = float
    TYPE_NAME = "float"

    @staticmethod
    def to_db_format(value: float) -> str:
        return str(value)

    @staticmethod
    def to_python_type(value: str) -> float:
        return float(value)


class StrDTypeConverter(DTypeConverter):
    PYTHON_TYPE = str
    TYPE_NAME = "string"

    @staticmethod
    def to_db_format(value: str) -> str:
        return value

    @staticmethod
    def to_python_type(value: str) -> str:
        return value


class NoneDTypeConverter(DTypeConverter):
    PYTHON_TYPE = type(None)
    TYPE_NAME = "none"

    @staticmethod
    def to_db_format(value: Any) -> str:
        return ""

    @staticmethod
    def to_python_type(value: str) -> None:
        return None


class BooleanDTypeConverter(DTypeConverter):
    PYTHON_TYPE = bool
    TYPE_NAME = "boolean"

    @staticmethod
    def to_db_format(value: bool) -> str:
        return str(value)

    @staticmethod
    def to_python_type(value: str) -> bool:
        if value == "True":
            converted_value = True
        else:
            converted_value = False
        return converted_value


class DatetimeDTypeConverter(DTypeConverter):
    PYTHON_TYPE = datetime
    TYPE_NAME = "datetime"

    @staticmethod
    def to_db_format(value: datetime) -> str:
        return value.isoformat()

    @staticmethod
    def to_python_type(value: str) -> datetime:
        return datetime.fromisoformat(value)


class TimedeltaDTypeConverter(DTypeConverter):
    PYTHON_TYPE = timedelta
    TYPE_NAME = "timedelta"

    @staticmethod
    def to_db_format(value: timedelta) -> str:
        return str(value.total_seconds())

    @staticmethod
    def to_python_type(value: str) -> timedelta:
        return timedelta(seconds=float(value))
