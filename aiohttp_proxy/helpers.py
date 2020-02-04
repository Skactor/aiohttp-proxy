# -*- coding: utf-8 -*-
import asyncio
import socket
from urllib.parse import unquote

from yarl import URL

from aiohttp_proxy.errors import ProxyError
from aiohttp_proxy.proto import Socks4SocketWrapper, Socks5SocketWrapper, ProxyType


def create_socket_wrapper(
    loop,
    proxy_type,
    host=None,
    port=None,
    username=None,
    password=None,
    rdns=True,
    family=socket.AF_INET,
):
    if proxy_type == ProxyType.SOCKS4:
        return Socks4SocketWrapper(
            loop=loop, host=host, port=port, user_id=username, rdns=rdns
        )
    elif proxy_type == ProxyType.SOCKS5:
        return Socks5SocketWrapper(
            loop=loop,
            host=host,
            port=port,
            username=username,
            password=password,
            rdns=rdns,
            family=family,
        )
    else:
        return None


def parse_proxy_url(raw_url):
    url = URL(raw_url)
    proxy_type = ProxyType(url.scheme)
    host = url.host
    if not host:
        raise ValueError("Empty host component")  # pragma: no cover
    try:
        port = int(url.port)
    except TypeError:  # pragma: no cover
        raise ValueError("Invalid port component")
    try:
        username, password = unquote(url.user), unquote(url.password)
    except TypeError:
        username, password = "", ""
    return proxy_type, host, port, username, password


async def open_connection(
    socks_url=None,
    host=None,
    port=None,
    *,
    proxy_type=ProxyType.SOCKS5,
    socks_host="127.0.0.1",
    socks_port=1080,
    username=None,
    password=None,
    rdns=True,
    family=socket.AF_INET,
    loop=None,
    **kwargs
):
    if host is None or port is None:
        raise ValueError("host and port must be specified")  # pragma: no cover

    if loop is None:
        loop = asyncio.get_event_loop()

    if socks_url is not None:
        proxy_type, socks_host, socks_port, username, password = parse_proxy_url(
            socks_url
        )

    sock = create_socket_wrapper(
        loop=loop,
        proxy_type=proxy_type,
        host=socks_host,
        port=socks_port,
        username=username,
        password=password,
        rdns=rdns,
        family=family,
    )
    if not sock:
        raise ProxyError("Only socks proxies are allowed to use `open_connection`")
    await sock.connect((host, port))

    return await asyncio.open_connection(loop=loop, sock=sock.socket, **kwargs)


async def create_connection(
    socks_url=None,
    protocol_factory=None,
    host=None,
    port=None,
    *,
    proxy_type=ProxyType.SOCKS5,
    socks_host="127.0.0.1",
    socks_port=1080,
    username=None,
    password=None,
    rdns=True,
    family=socket.AF_INET,
    loop=None,
    **kwargs
):
    if protocol_factory is None:
        raise ValueError("protocol_factory " "must be specified")  # pragma: no cover

    if host is None or port is None:
        raise ValueError("host and port " "must be specified")  # pragma: no cover

    if loop is None:
        loop = asyncio.get_event_loop()

    if socks_url is not None:
        proxy_type, socks_host, socks_port, username, password = parse_proxy_url(
            socks_url
        )

    sock = create_socket_wrapper(
        loop=loop,
        proxy_type=proxy_type,
        host=socks_host,
        port=socks_port,
        username=username,
        password=password,
        rdns=rdns,
        family=family,
    )
    if not sock:
        raise ProxyError("Only socks proxies are allowed to use `create_connection`")
    await sock.connect((host, port))

    return await loop.create_connection(
        protocol_factory=protocol_factory, sock=sock.socket, **kwargs
    )
