import contextvars

import ulid

request_id: contextvars.ContextVar = contextvars.ContextVar("request_id", default=ulid.new().str)
user_id: contextvars.ContextVar = contextvars.ContextVar("user_id", default=0)


def rid_get() -> str:
    return request_id.get()


def rid_set(id: str) -> int:
    request_id.set(id)
    return 0


def uid_get() -> int:
    return user_id.get()


def uid_set(id: int) -> int:
    user_id.set(id)
    return 0