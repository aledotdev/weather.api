import os

from tornado import web

from .views.weather import ExploreHandler
from .views.map import MapHandler
from .views import RedisCacheManager



def make_app(options):
    routes = [
        (r"/static/(.*)", web.StaticFileHandler,
         {"path": get_current_path('static/')}),
        (r'/api/v1/weather/current/', ExploreHandler),
        (r'/map/?', MapHandler)
    ]
    app = web.Application(
        routes,debug=bool(options.debug))

    app.settings['template_path'] = get_current_path('templates/')
    app.cache = RedisCacheManager()
    return app


def get_current_path(*args):
    path = os.path.dirname(__file__)
    if args:
        paths = [path] + list(args)
        path = os.path.join(*paths)
    return path
