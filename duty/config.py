import logging
import os
from dataclasses import MISSING, dataclass, fields
from typing import Optional


@dataclass
class EnvConfig:
    IRCA_DB_URL: Optional[str]
    IRCA_LOG_LEVEL: Optional[str]
    IRCA_LOG_FILE: Optional[str]
    "Empty string or path to file"
    IRCA_LOG_STDOUT: bool = False
    "Whether log to stdout"


@dataclass
class Config:
    db_url: Optional[str]
    log_level: int
    log_file: Optional[str]
    log_stdout: bool


class ConfigParseError(Exception):
    pass


def parse_log_level(value: 'str | None') -> int:
    if value is None:
        return logging.DEBUG

    return {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR
    }.get(value.strip().lower(), logging.INFO)


def parse_bool(value: 'str | None', default):
    if value is None:
        assert isinstance(default, bool)
        return default

    if value.lower() in ('true', '1'):
        return True
    if value.lower() in ('false', '0'):
        return False
    raise ConfigParseError('Bool env variable must be "true", '
                           f'"false", "1" or "0", not {value!r}')

def load_from_env() -> Config:
    params = {}
    for field in fields(EnvConfig):
        default = None
        if field.default is not MISSING:
            default = field.default
        value = os.getenv(field.name, default)
        if field.type is bool:
            value = parse_bool(value, default)
        params[field.name] = value
    env_config = EnvConfig(**params)

    return Config(
        db_url=env_config.IRCA_DB_URL,
        log_level=parse_log_level(env_config.IRCA_LOG_LEVEL),
        log_file=env_config.IRCA_LOG_FILE,
        log_stdout=env_config.IRCA_LOG_STDOUT
    )
