from tornado.options import define

define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
	"""docstring for Application"""
	def __init__(self, arg):
		super(Application, self).__init__()
		self.arg = arg
		