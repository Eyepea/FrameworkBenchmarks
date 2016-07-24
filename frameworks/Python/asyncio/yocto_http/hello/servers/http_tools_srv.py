import argparse
import asyncio
import aiohttp
import aiohttp.server
import ujson
from aiohttp import web
import sys

import httptools

from socket import *


class HttpRequest:
    __slots__ = ('_protocol', '_url', '_headers', '_version')

    def __init__(self, protocol, url, headers, version):
        self._protocol = protocol
        self._url = url
        self._headers = headers
        self._version = version


class HttpResponse:
    __slots__ = ('_protocol', '_request', '_headers_sent')

    def __init__(self, protocol, request):
        self._protocol = protocol
        self._request = request
        self._headers_sent = False

    def write(self, data):
        self._protocol._transport.write(b''.join([
            'HTTP/{} 200 OK\r\n'.format(
                self._request._version).encode('latin-1'),
            b'Content-Type: text/plain\r\n',
            'Content-Length: {}\r\n'.format(len(data)).encode('latin-1'),
            b'\r\n',
            data
        ]))


class HttpProtocol(asyncio.Protocol):

    __slots__ = ('_loop',
                 '_transport', '_current_request', '_current_parser',
                 '_current_url', '_current_headers')

    def __init__(self, *, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop
        self._transport = None
        self._current_request = None
        self._current_parser = None
        self._current_url = None
        self._current_headers = None

    def on_url(self, url):
        self._current_url = url

    def on_header(self, name, value):
        self._current_headers.append((name, value))

    def on_headers_complete(self):
        self._current_request = HttpRequest(
            self, self._current_url, self._current_headers,
            self._current_parser.get_http_version())

        self._loop.call_soon(
            self.handle, self._current_request,
            HttpResponse(self, self._current_request))

    ####

    def connection_made(self, transport):
        self._transport = transport
        sock = transport.get_extra_info('socket')
        try:
            sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
        except (OSError, NameError):
            pass

    def connection_lost(self, exc):
        self._current_request = self._current_parser = None

    def data_received(self, data):
        if self._current_parser is None:
            assert self._current_request is None
            self._current_headers = []
            self._current_parser = httptools.HttpRequestParser(self)

        self._current_parser.feed_data(data)

    def handle(self, request, response):
        parsed_url = httptools.parse_url(self._current_url)
        response.write(ujson.dumps({'message': 'Hello, World!'}).encode('utf-8'))
        if not self._current_parser.should_keep_alive():
            self._transport.close()
        self._current_parser = None
        self._current_request = None
