#!/usr/bin/env python

"""
An HTTP & web socket server that reads from a TLS server stream and writes all
data to connected web socket clients.
"""

import os
import logging
import socket

from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.web import asynchronous
from tornado.iostream import SSLIOStream
from tornado.ioloop import IOLoop
from tornado import options

from lib.stream_reader import StreamReader


log = logging.getLogger(__name__)
port = 8080
tls_host = 'localhost'
tls_port = 4443


class FeedHandler(RequestHandler):
    feed = StreamReader(tls_host, tls_port)

    @asynchronous
    def get(self):
        FeedHandler.feed.add(self)

    def on_connection_close(self):
        FeedHandler.feed.remove(self)


routes = [
    (r'/', StaticFileHandler,
        {'path': os.path.join(os.path.dirname(__file__), 'index.html')}),
    (r'/feed', FeedHandler)
]

if __name__ == "__main__":
    options.parse_command_line()
    application = Application(routes)
    application.listen(port)
    log.info('Listening on port %d...', port)
    IOLoop.instance().start()
