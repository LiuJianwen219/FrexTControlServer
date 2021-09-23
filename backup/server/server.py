import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
from tornado.options import define, options

define("port", default=8014, help="run on the given port ", type=int)
define("log_path", default='/tmp', help="log path ", type=str)

from backup.server.help import HelpHandler
from backup.server.health import HealthHandler



class ControlServer:
    def __init__(self, configs):
        print("config control server")
        print(configs)
        print(options.port)
        print(options.log_path)

    def init_control_server(self):
        print("init control server")
        tornado.options.parse_command_line()
        app = tornado.web.Application(handlers=[
            (r"/help/", HelpHandler),
            (r"/ping/", HealthHandler),
            (r"/", HelpHandler),
        ])
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(options.port)

    def run(self):
        print("run control server")
        tornado.ioloop.IOLoop.instance().start()
