from pydantic import BaseModel, ConfigDict

from . import models
from .queue import get_client

rabbit_client = get_client()


class Event(BaseModel):
    name: str
    params: dict


class UserUpdated(BaseModel):
    model_config = ConfigDict(extra='allow')

    user_id: int
    email: str
    username: str
    roles: str


@rabbit_client.add_handler('UserUpdated')
def on_user_updated(message):
    event = Event.model_validate(message)
    user_updated = UserUpdated.model_validate(event.params)

    models.User.objects.update_or_create(
        user_id=user_updated.user_id,
        defaults={
            'username': user_updated.username,
            'roles': user_updated.roles,
        },
    )

