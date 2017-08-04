import json

from tornado import web, gen
from tornado_cors import CorsMixin

from ..libs import coords
from . import OWMHandlerMixin


class ExploreHandler(CorsMixin, web.RequestHandler, OWMHandlerMixin):

    CORS_ORIGIN = '*'

    @gen.coroutine
    def get(self):
        ll_ne = coords.parse_location(self.get_argument('ll_ne'))
        ll_sw = coords.parse_location(self.get_argument('ll_sw'))
        zoom = int(self.get_argument('zoom', 9))

        owm_zoom = coords.get_owm_zoom(zoom)
        grid = coords.get_bbox_area_grid(ll_ne, ll_sw, owm_zoom)

        data = yield self.owm_grid_explore(grid, owm_zoom['owm_zoom'])

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(data))
        self.finish()
