from dataclasses import dataclass


# Services used for this test
class Config:
    pass


@dataclass
class Database:
    config: Config


@dataclass
class Cache:
    config: Config


@dataclass
class HTTPClient:
    config: Config


@dataclass
class BarService:
    config: Config
    database: Database
    cache: Cache
    http_client: HTTPClient


@dataclass
class FooService:
    config: Config
    database: Database
    cache: Cache
    http_client: HTTPClient
    bar_service: BarService
