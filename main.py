import tornado.web
import tornado.websocket
from tornado.options import define, options
from matplotlib.backends.backend_webagg_core import (FigureManagerWebAgg, new_figure_manager_given_figure)
from matplotlib.figure import Figure
import numpy as np
import json
import os
import io

define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self, figure):
        self.figure = figure
        self.manager = new_figure_manager_given_figure(id(figure), figure)

        handlers = [(r'/_static/(.*)',tornado.web.StaticFileHandler,{'path': FigureManagerWebAgg.get_static_file_path()}),
                    (r"/", self.MainHandler), 
                    (r"/ws", self.SocketHandler),
                    (r'/download.([a-z0-9.]+)', self.Download),
                    ('/mpl.js', self.MplJs)]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        super(Application, self).__init__(handlers, **settings)

    class Download(tornado.web.RequestHandler):
        def get(self, fmt):
            manager = self.application.manager

            mimetypes = {
                'ps': 'application/postscript',
                'eps': 'application/postscript',
                'pdf': 'application/pdf',
                'svg': 'image/svg+xml',
                'png': 'image/png',
                'jpeg': 'image/jpeg',
                'tif': 'image/tiff',
                'emf': 'application/emf'
            }

            self.set_header('Content-Type', mimetypes.get(fmt, 'binary'))

            buff = io.BytesIO()
            manager.canvas.figure.savefig(buff, format=fmt)
            self.write(buff.getvalue())

    class MplJs(tornado.web.RequestHandler):
        def get(self):
            self.set_header('Content-Type', 'application/javascript')
            js_content = FigureManagerWebAgg.get_javascript()
            # print(js_content)
            self.write(js_content)

    class MainHandler(tornado.web.RequestHandler):
        def get(self):
            manager = self.application.manager
            ws_uri = "ws://{req.host}/".format(req=self.request) + "ws"
            # chat = {"ws_uri": ws_uri, "fig_id": manager.num}
            self.render("index.html", ws_uri=ws_uri, fig_id=manager.num)

    class SocketHandler(tornado.websocket.WebSocketHandler):
        supports_binary = True
        def open(self):
            # Register the websocket with the FigureManager.
            manager = self.application.manager
            manager.add_web_socket(self)
            if hasattr(self, 'set_nodelay'):
                self.set_nodelay(True)

        def on_close(self):
            manager = self.application.manager
            manager.remove_web_socket(self)

        def on_message(self, message):
            message = json.loads(message)
            if message['type'] == 'supports_binary':
                self.supports_binary = message['value']
            else:
                manager = self.application.manager
                manager.handle_json(message)

        def send_json(self, content):
            self.write_message(json.dumps(content))

        def send_binary(self, blob):
            if self.supports_binary:
                self.write_message(blob, binary=True)
            else:
                data_uri = "data:image/png;base64,{0}".format(
                    blob.encode('base64').replace('\n', ''))
                self.write_message(data_uri)


def create_figure():
    """
    Creates a simple example figure.
    """
    fig = Figure()
    a = fig.add_subplot(111)
    t = np.arange(0.0, 3.0, 0.01)
    s = np.sin(2 * np.pi * t)
    a.plot(t, s)
    return fig

def main():
    figure = create_figure()
    tornado.options.parse_command_line()
    application = Application(figure)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()

