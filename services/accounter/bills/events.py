from pydantic import BaseModel

from .queue import get_client

rabbit_client = get_client()


class Event(BaseModel):
    name: str
    params: dict
