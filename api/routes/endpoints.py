from dataclasses import dataclass


@dataclass
class ApiEndpoints:
    PING: str = "/ping"
    HEALTH: str = "/health"
    ANONYMIZE: str = "/anonymize"


endpoints = ApiEndpoints()
