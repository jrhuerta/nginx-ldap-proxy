#!/usr/bin/env python
import logging
import os

import bonsai
from aiohttp import BasicAuth, hdrs, web
from multidict import istr

logging.basicConfig(level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO")))

routes = web.RouteTableDef()


class LDAP_HEADERS:
    URI = istr("x-ldap-uri")
    USER_DN_TEMPLATE = istr("x-ldap-user-dn-tpl")


def challenge_response() -> web.Response:
    return web.Response(
        status=401,
        headers={
            "WWW-Authenticate": "Basic "
            "realm=AlayaCare "
            "documentation "
            "site, "
            'charset="UTF-8"'
        },
    )


@routes.get("/auth")
async def ldap_auth(request: web.Request) -> web.Response:
    ldap_uri = request.headers.get(LDAP_HEADERS.URI)
    ldap_user_dn_tpl = request.headers.get(LDAP_HEADERS.USER_DN_TEMPLATE)
    if not (ldap_uri and ldap_user_dn_tpl):
        logging.error("LDAP configuration headers missing.")
        return web.Response(status=400)

    auth_header = request.headers.get(hdrs.AUTHORIZATION)
    if not auth_header:
        logging.debug("Authorization header missing.")
        return challenge_response()
    auth = BasicAuth.decode(auth_header=auth_header, encoding="UTF-8")

    client = bonsai.LDAPClient(ldap_uri)
    client.set_credentials(
        "SIMPLE", user=ldap_user_dn_tpl.format(user=auth.login), password=auth.password
    )
    try:
        async with client.connect(is_async=True) as conn:
            await conn.whoami()
            return web.Response(
                status=204, headers={"Cache-Control": "public, max-age=1800"}
            )
    except bonsai.AuthenticationError as ex:
        logging.debug(repr(ex))
        return challenge_response()


async def app() -> web.Application:
    app = web.Application()
    app.add_routes(routes)
    return app


if __name__ == "__main__":
    web.run_app(app())
