from tornado import web

from .views.weather import ExploreHandler
from .views import RedisCacheManager

def make_app(options):
    routes = [
        (r'/api/v1/weather/current/', ExploreHandler)
    ]
    app = web.Application(routes, debug=bool(options.debug))
    app.cache = RedisCacheManager()
    return app
