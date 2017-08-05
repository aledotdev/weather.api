import json

from tornado import httpclient
from tornado.httputil import url_concat
import requests

from .. import settings

httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient",
                                     max_clients=settings.OWM_HTTP_CLIENT_CONN)


class OWMException(Exception):
    response = None


OWM_URL = 'http://api.openweathermap.org'
STATIONS_BY_BBOX = '/data/2.5/box/city'

class OWM(object):

    version = '2.5'

    def __init__(self, async=False):
        self.async = async

    def api_get(self, path, params):
        """ If sync == True returns a Future object.
        """
        base_url = '{}{}'.format(OWM_URL, path)
        # Set OWM application secret key to auth
        params['appid'] = settings.OWM_API_KEY
        url = url_concat(base_url, params)

        if self.async:
            http_client = httpclient.AsyncHTTPClient()
            request = httpclient.HTTPRequest(
                url, request_timeout=settings.OWM_REQUEST_TIMEOUT,
                connect_timeout=settings.OWM_CONN_TIMEOUT)

            return http_client.fetch(request, raise_error=False)
        else:
            return requests.get(url)

    def get_stations_by_bbox(self, lng_left, lat_bottom, lng_right, lat_top,
                             zoom=None, cluster=False):

        bbox_params = [lng_left, lat_bottom, lng_right, lat_top]
        if zoom is not None:
            bbox_params.append(zoom)

        params = {
            'bbox': ','.join([str(p) for p in bbox_params]),
            'cluster': 'yes' if cluster is True else 'no',
        }

        return self.api_get(STATIONS_BY_BBOX, params)

    def parse(self, raw_data):
        data = json.loads(raw_data)

        if 'list' in data:
            return data['list']

        return []
