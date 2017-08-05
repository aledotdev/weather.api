from tornado import web
from tornado_cors import CorsMixin


class MapHandler(CorsMixin, web.RequestHandler,):

    CORS_ORIGIN = '*'

    def get(self):
        self.render('map.html')
