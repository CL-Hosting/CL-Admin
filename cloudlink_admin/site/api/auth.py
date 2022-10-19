from __future__ import annotations


import time

from multipledispatch import dispatch
from sanic.response import json, HTTPResponse


@dispatch(callable)
def protected(func: callable[HTTPResponse]) -> callable[HTTPResponse]:  # type: ignore[type-arg]
    def inner(req, *args, **kwargs) -> HTTPResponse:
        if not req.token:
            return json(
                {"type": "AuthError", "error": "No token provided", "status": 401},
                status=401,
            )
        usr = req.ctx.db.users.find_one({"session": {"token": req.token}})
        if not usr:
            return json(
                {"type": "AuthError", "error": "Invalid token", "status": 401},
                status=401,
            )

        # check if timout is less then 45 minutes
        if (time.time() - usr["session"]["timeout"]) < (60 * 45):
            # clear the token
            req.ctx.db.users.update_one(
                {"session": {"token": req.token}},
                {
                    "$set": {
                        "session": {"timeout": 0, "token": None, "refresh_token": None}
                    }
                },
            )

            return json(
                {"type": "AuthError", "error": "Login has expired", "status": 401},
                status=401,
            )

        if not usr.get("level", 0) >= 2:
            return json(
                {
                    "type": "AuthError",
                    "error": "Insufficient permissions",
                    "status": 401,
                },
                status=401,
            )

        req.ctx.user = usr
        return func(req, *args, **kwargs)

    return inner


@protected.register(int)
def _(lvl:int) -> callable[callable[HTTPResponse]]:  # type: ignore[type-arg]
    def inner(func: callable[HTTPResponse]) -> callable[HTTPResponse]:  # type: ignore[type-arg]
        def wrapper(req, *args, **kwargs):
            if not req.token:
                return json(
                    {"type": "AuthError", "error": "No token provided", "status": 401},
                    status=401,
                )
            usr = req.ctx.db.users.find_one({"session": {"token": req.token}})
            if not usr:
                return json(
                    {"type": "AuthError", "error": "Invalid token", "status": 401},
                    status=401,
                )

            # check if timout is less then 45 minutes
            if (time.time() - usr["session"]["timeout"]) < (60 * 45):
                # clear the token
                req.ctx.db.users.update_one(
                    {"session": {"token": req.token}},
                    {
                        "$set": {
                            "session": {
                                "timeout": 0,
                                "token": None,
                                "refresh_token": None,
                            }
                        }
                    },
                )
                return json(
                    {"type": "AuthError", "error": "Login has expired", "status": 401},
                    status=401,
                )

            if not usr.get("level", 0) <= lvl:
                return json(
                    {
                        "type": "AuthError",
                        "error": "Insufficient permissions",
                        "status": 401,
                    },
                    status=401,
                )

            return func(req, *args, **kwargs)

        return wrapper

    return inner


__all__ = ["protected"]
