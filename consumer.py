#!/usr/bin/env python

"""
An HTTP & web socket server that reads from a TLS server stream and writes all
data to connected web socket clients.
"""

import logging
import socket

from tornado.web import Application, RequestHandler, asynchronous
from tornado.iostream import SSLIOStream
from tornado.ioloop import IOLoop
from tornado import options


log = logging.getLogger(__name__)
port = 8080
tls_server = ('localhost', 4443)


class TestHandler(RequestHandler):
    @asynchronous
    def get(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.tls_client = SSLIOStream(s)
        self.tls_client.connect(tls_server)
        self.tls_client.read_until("\n", self._write_data)

    def _write_data(self, d):
        log.debug('Received data:  %s', str(d))
        self.write(str(d))
        self.flush()
        self.tls_client.read_until("\n", self._write_data)

    def on_connection_close(self):
        self.tls_client.close()


routes = [
    (r'/', TestHandler)
]

if __name__ == "__main__":
    options.parse_command_line()
    application = Application(routes)
    application.listen(port)
    IOLoop.instance().start()
