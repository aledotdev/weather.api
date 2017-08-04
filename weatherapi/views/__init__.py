import json
import re

from tornado import gen
import tornadoredis
from weatherapi.libs.owm import OWM

from .. import settings

GRID_CACHE_KEY = 'owm:grid:bbox:{}'


class OWMHandlerMixin(object):

    @property
    def owm(self):
        if not hasattr(self, '_owm'):
            self._owm = OWM(async=True)
        return self._owm

    @gen.coroutine
    def owm_grid_explore(self, grids, zoom, cluster=False):
        calls = {}
        bbhash_keys = [GRID_CACHE_KEY.format(bbhash) for bbhash, box in grids]
        cached = yield self.application.cache.obj_mget(bbhash_keys)

        for index, grid in enumerate(grids):
            bbhash, bbox = grid
            if cached[index] is not None:
                continue

            calls[bbhash] = self.owm.get_stations_by_bbox(
                bbox.sw.lng, bbox.sw.lat, bbox.ne.lng, bbox.ne.lat,
                zoom=zoom, cluster=cluster)

        responses = yield calls

        data = []
        for bbhash, response in responses.items():
            items = self.owm.parse(response.body.decode())
            resp_data = []
            for item in items:
                resp_data.append(self.format_weather(item))

            self.application.cache.obj_set(GRID_CACHE_KEY.format(bbhash),
                                           resp_data, 60*60)
            data.extend(resp_data)

        for cached_data in cached:
            if cached_data is None:
                continue
            data.extend(cached_data)

        return data

    def format_weather(self, data):
        weather = data['weather'][0]
        icon_name = weather['icon']
        # Use the same icons for day and night
        icon_name = re.sub(r'n$', 'd', icon_name)
        return dict(
            location=[data['coord']['Lat'], data['coord']['Lon']],
            location_name=data['name'],
            weather={
                'status': weather['main'],
                'title': weather['description'],
                'icon': "%s/%s.png" % (settings.OWM_ICON_URL, icon_name),
                'temperature': {
                    'current': data['main']['temp'],
                },
            },
            date=data['dt']
        )


class RedisCacheManager(object):

    @property
    def client(self):
        if not hasattr(self, '_client'):
            self._client = tornadoredis.Client()
        return self._client

    @gen.coroutine
    def get(self, key):
        value = yield gen.Task(self.client.get, key)
        return value

    @gen.coroutine
    def mget(self, keys):
        values = yield gen.Task(self.client.mget, keys)
        return values

    @gen.coroutine
    def set(self, key, value, expire=60):
        pipe = self.client.pipeline()
        value = value
        pipe.set(key, value)
        pipe.expire(key, expire)
        res_hset, res_expire = yield gen.Task(pipe.execute)

    @gen.coroutine
    def obj_set(self, key, value, expire=60):
        value = json.dumps(value)
        value = yield self.set(key, value, expire)

    @gen.coroutine
    def obj_mget(self, keys):
        values = yield self.mget(keys)
        data = []
        for v in values:
            if v is None:
                data.append(None)
            else:
                data.append(json.loads(v))
        return data

    @gen.coroutine
    def obj_get(self, key):
        value = yield self.get(key)
        if value is not None:
            value = json.loads(value)
        return value
