from functools import lru_cache

from keycloak import KeycloakAdmin


@lru_cache
def get_admin():
    return KeycloakAdmin(
        server_url="http://keycloack:8080/",  # TODO: provision config via env variables
        username='admin',
        password='admin_pass',
        realm_name="master",
    )


def create_user(
    email: str,
    username: str,
    password: str,
    roles: list[str],
) -> dict:
    return get_admin().create_user(
        {
            'email': email,
            'username': username,
            'enabled': True,
            'credentials': [{'value': password, 'type': 'password', }],
            'groups': roles,
        },
        exist_ok=True,
    )
