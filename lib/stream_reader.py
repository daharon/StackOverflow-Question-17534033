import logging
import socket

from tornado.tcpclient import TCPClient
from tornado.gen import coroutine, Task


log = logging.getLogger(__name__)


class SSLStreamReader:
    def __init__(self, host, port):
        self._port = port
        self._host = host
        self._stream = None
        self._clients = set()

    @coroutine
    def add(self, client):
        self._clients.add(client)
        log.debug('Added client %s', client)
        if self._stream is None:
            yield self._connect()
            self._read_stream()

    def remove(self, client):
        self._clients.remove(client)
        log.debug('Removed client %s', client)

    @staticmethod
    def process(data):
        return data

    @staticmethod
    def write_message(client, data):
        pass

    @coroutine
    def _connect(self):
        log.debug('Connecting to %s:%d', self._host, self._port)
        ssl_options = {}
        self._stream = yield TCPClient().connect(self._host, self._port,
                                                 socket.AF_INET, ssl_options)

    def _disconnect(self):
        self._stream.close()
        self._stream = None
        log.debug('Disconnected from %s:%d', self._host, self._port)

    @coroutine
    def _read_stream(self):
        log.debug('Reading stream from %s:%d', self._host, self._port)
        while self._clients:
            data = yield Task(self._stream.read_until, b"\n")
            output = self.process(data.decode('utf-8'))
            for client in self._clients:
                self.write_message(client, output)
        self._disconnect()
        return
