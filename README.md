## aiohttp-proxy

[![Build Status](https://travis-ci.org/Skactor/aiohttp-proxy.svg?branch=master)](https://github.com/Skactor/aiohttp-proxy)
[![Coverage Status](https://coveralls.io/repos/github/Skactor/aiohttp-proxy/badge.svg?branch=master)](https://coveralls.io/Skactor/aiohttp-proxy?branch=master)
[![PyPI version](https://badge.fury.io/py/aiohttp-proxy.svg)](https://badge.fury.io/py/aiohttp-proxy)

SOCKS proxy connector for [aiohttp](https://github.com/aio-libs/aiohttp). HTTP, HTTPS, SOCKS4(a) and SOCKS5(h) proxies are supported.

## Requirements
- Python >= 3.5.3
- aiohttp >= 2.3.2  # including v3.x

## Installation
```
pip install aiohttp_proxy
```

## Usage

#### aiohttp usage:
```python
import aiohttp
from aiohttp_proxy import ProxyConnector, ProxyType


async def fetch(url):
    connector = ProxyConnector.from_url('http://user:password@127.0.0.1:1080')
    ### or use ProxyConnector constructor
    # connector = ProxyConnector(
    #     proxy_type=ProxyType.SOCKS5,
    #     host='127.0.0.1',
    #     port=1080,
    #     username='user',
    #     password='password',
    #     rdns=True
    # )
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as response:
            return await response.text()
```

#### aiohttp-socks also provides `open_connection` and `create_connection` functions:

```python
from aiohttp_proxy import open_connection

async def fetch():
    reader, writer = await open_connection(
        socks_url='http://user:password@127.0.0.1:1080',
        host='check-host.net',
        port=80
    )
    request = (b"GET /ip HTTP/1.1\r\n"
               b"Host: check-host.net\r\n"
               b"Connection: close\r\n\r\n")

    writer.write(request)
    return await reader.read(-1)
```

## Why give aiohttp a new proxy support

First must declare, our code is based on [aiohttp-socks](https://github.com/romis2012/aiohttp-socks), thank you very much for the hard work.

But in order to more flexible support for multiple proxy methods (not just SOCKS proxy),
we decided to fork [aiohttp-socks] (https://github.com/romis2012/aiohttp-socks), which is currently based on it.

Combine with native aiohttp to provide HTTP/HTTPS proxy instead of writing troublesome discriminating code based on the type of proxy.