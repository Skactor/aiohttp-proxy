import socket

from aiohttp import TCPConnector
from aiohttp.abc import AbstractResolver
from yarl import URL

from .helpers import create_socket_wrapper, parse_proxy_url
from .proto import ProxyType


class NoResolver(AbstractResolver):
    async def resolve(self, host, port=0, family=socket.AF_INET):
        return [
            {
                "hostname": host,
                "host": host,
                "port": port,
                "family": family,
                "proto": 0,
                "flags": 0,
            }
        ]

    async def close(self):
        pass  # pragma: no cover


class ProxyConnector(TCPConnector):
    def __init__(
        self,
        proxy_type=ProxyType.HTTP,
        host=None,
        port=None,
        username=None,
        password=None,
        rdns=False,
        family=socket.AF_INET,
        **kwargs
    ):

        if rdns:
            kwargs["resolver"] = NoResolver()

        super().__init__(**kwargs)

        self._proxy_type = proxy_type
        self._proxy_host = host
        self._proxy_port = port
        self._proxy_username = username
        self._proxy_password = password
        self._rdns = rdns
        self._proxy_family = family

    @property
    def proxy_url(self):
        if self._proxy_username:
            url_tpl = "{scheme}://{username}:{password}@{host}:{port}"
        else:
            url_tpl = "{scheme}://{host}:{port}"

        url = url_tpl.format(
            scheme=self._proxy_type,
            username=self._proxy_username,
            password=self._proxy_password,
            host=self._proxy_host,
            port=self._proxy_port,
        )
        return URL(url)

    # noinspection PyMethodOverriding
    async def _wrap_create_connection(
        self, protocol_factory, host=None, port=None, *args, **kwargs
    ):
        if not self._proxy_type.is_http():
            sock = create_socket_wrapper(
                loop=self._loop,
                proxy_type=self._proxy_type,
                host=self._proxy_host,
                port=self._proxy_port,
                username=self._proxy_username,
                password=self._proxy_password,
                rdns=self._rdns,
                family=self._proxy_family,
            )
            await sock.connect((host, port))

            return await super()._wrap_create_connection(
                protocol_factory, None, None, *args, sock=sock.socket, **kwargs
            )
        else:
            return await super(ProxyConnector, self)._wrap_create_connection(
                protocol_factory, host, port, *args, **kwargs
            )

    async def connect(self, req, traces, timeout):
        if self._proxy_type.is_http():
            req.update_proxy(
                self.proxy_url.with_scheme("http"), None, req.proxy_headers
            )
        return await super(ProxyConnector, self).connect(
            req=req, traces=traces, timeout=timeout
        )

    @classmethod
    def from_url(cls, url, **kwargs):
        proxy_type, host, port, username, password = parse_proxy_url(url)
        return cls(
            proxy_type=proxy_type,
            host=host,
            port=port,
            username=username,
            password=password,
            **kwargs
        )
