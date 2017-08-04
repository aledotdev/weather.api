import tornado.web
import tornado.httpserver
from tornado.options import options
from weatherapi import settings


from weatherapi.app import make_app

options.define('port', settings.PORT)
options.define('debug', settings.DEBUG)


def run_server():
    options.parse_command_line()
    app = make_app(options)
    app.listen(options.port)

    #server = tornado.httpserver.HTTPServer(app, max_buffer_size=1024*1024*201)
    #server.bind(settings.PORT)
    #server.start(0)

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()

if __name__ == '__main__':
    run_server()
