#!/usr/bin/env python3

"""
An HTTP & web socket server that reads from a TLS server stream and writes all
data to connected web socket clients.
"""

import os
import logging
from datetime import datetime

from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler
from tornado.ioloop import IOLoop
from tornado import options

from lib.stream_reader import SSLStreamReader


log = logging.getLogger(__name__)
port = 8080
tls_host = 'localhost'
tls_port = 4443


class CustomReader(SSLStreamReader):
    @staticmethod
    def process(data):
        return "%s - %s" % (datetime.now(), str(data))

    @staticmethod
    def write_message(client, data):
        client.write_message(data)


class RootHandler(RequestHandler):
    def get(self):
        self.render('index.html')


class FeedHandler(WebSocketHandler):
    feed = CustomReader(tls_host, tls_port)

    def open(self):
        FeedHandler.feed.add(self)

    def on_close(self):
        FeedHandler.feed.remove(self)


settings = {
    'template_path': os.path.join(os.path.dirname(__file__), 'html'),
    'debug': True
}
routes = [
    (r'/', RootHandler),
    (r'/feed', FeedHandler)
]

if __name__ == "__main__":
    options.parse_command_line()
    application = Application(routes, **settings)
    application.listen(port)
    log.info('Listening on port %d...', port)
    try:
        IOLoop.instance().start()
    except (KeyboardInterrupt, SystemExit):
        pass
