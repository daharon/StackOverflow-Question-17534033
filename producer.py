#!/usr/bin/env python3

""" A TLS server that spits out random md5 hashes every half second. """

import os
import ssl
from hashlib import md5
import logging

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.tcpserver import TCPServer
from tornado import options


log = logging.getLogger(__name__)
port = 4443
ssl_options = {
    'ssl_version': ssl.PROTOCOL_TLSv1,
    'certfile': os.path.join(os.path.dirname(__file__), 'server.crt'),
    'keyfile': os.path.join(os.path.dirname(__file__), 'server.key')
}


class RandomServer(TCPServer):
    def handle_stream(self, stream, address):
        SpitRandomStuff(stream, address)


class SpitRandomStuff:
    def __init__(self, stream, address):
        log.info('Received connection from %s', address)
        self.address = address
        self.stream = stream
        self.stream.set_close_callback(self._on_close)
        self.writer = PeriodicCallback(self._random_stuff, 500)
        self.writer.start()

    def _on_close(self):
        log.info('Closed connection from %s', self.address)
        self.writer.stop()

    def _random_stuff(self):
        random_num = os.urandom(60)
        random_str = md5(random_num).hexdigest() + "\n"
        output = random_str.encode('utf-8')  # str -> bytes
        self.stream.write(output)


if __name__ == '__main__':
    options.parse_command_line()
    server = RandomServer(ssl_options=ssl_options)
    server.listen(port)
    log.info('Listening on port %d...', port)
    try:
        IOLoop.instance().start()
    except (KeyboardInterrupt, SystemExit):
        pass
