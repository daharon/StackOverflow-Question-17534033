import logging
import socket

from tornado.iostream import SSLIOStream
from tornado.gen import coroutine, Task


log = logging.getLogger(__name__)


class SSLStreamReader:
    def __init__(self, host, port):
        self._address = (host, port)
        self._stream = None
        self._clients = set()

    def add(self, client):
        self._clients.add(client)
        log.debug('Added client %s', client)
        if self._stream is None:
            self._connect()
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

    def _connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self._stream = SSLIOStream(s)
        log.debug('Connecting to %s', self._address)
        self._stream.connect(self._address)

    def _disconnect(self):
        self._stream.close()
        self._stream = None
        log.debug('Disconnected from %s', self._address)

    @coroutine
    def _read_stream(self):
        log.debug('Reading stream from %s', self._address)
        while self._clients:
            data = yield Task(self._stream.read_until, b"\n")
            output = self.process(data.decode('utf-8'))
            for client in self._clients:
                self.write_message(client, output)
        self._disconnect()
        return
