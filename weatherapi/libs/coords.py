# -*- coding: utf-8 -*-

import bisect
from collections import namedtuple
from itertools import product

import geohash

def set_owm_zoom_grid():
    _OWM_ZOOM = {
        (1,6): {'owm_zoom': 3, 'hash_precision': 1},
        (7,10): {'owm_zoom': 8, 'hash_precision': 2},
        (11,20): {'owm_zoom': 15, 'hash_precision': 3}
    }
    HASH_SIZE_INDEXES = [1, 2, 5, 7, 10, 12, 15, 17]

    for zrange, data in _OWM_ZOOM.items():
        """
        HASH_SIZE_INDEXES are the constants to calculate the Geohash precision.
        https://en.wikipedia.org/wiki/Geohash
        """

        hash_precision = data['hash_precision']
        hash_size_index = HASH_SIZE_INDEXES[hash_precision]

        lat_len = lng_len = 2**hash_size_index
        if hash_precision % 2 == 1:
            lng_len = 2**(hash_size_index+1)

        data['distance'] = (lat_len, lng_len)

        data['lats'] = [180.0 * i / lat_len for i in range((lat_len//-2)-1, (lat_len//2)+1)]
        #Geohash crash with latitudes greater than 85
        data['lats'][0] = -85.0
        data['lats'][-1] = 85.0
        data['lngs'] = [360.0 * i / lng_len for i in range((lng_len//-2)-1, (lng_len//2)+1)]

    return _OWM_ZOOM

OWM_ZOOM = set_owm_zoom_grid()

LocationTuple = namedtuple('LocationTuple', 'lat,lng,tuple,text,geohash')
BboxTuple = namedtuple('BboxTuple', 'ne,sw')


def parse_location(*args):
    if isinstance(args[0], LocationTuple):
        return args[0]

    lat = None
    lng = None
    if len(args) == 2:
        lat = args[0]
        lng = args[1]
    else:
        arg = args[0]
        if type(arg) in [tuple, list]:
            lat = arg[0]
            lng = arg[1]
        elif ',' in arg:
            lat, lng = arg.split(',')

    lat = float(lat)
    if lat > 85:
        lat = 85.0
    lng = float(lng)

    return LocationTuple(lat, lng, (lat, lng), "%s,%s" % (lat, lng),
                         geohash.encode(lat, lng))

def parse_bbox(*args):
    ne = None
    sw = None

    if len(args) == 4:
        ne = LocationTuple(args[0], args[1])
        sw = LocationTuple(args[2], args[3])
    elif isinstance(args[0], dict):
        ne = parse_location(args[0]['n'], args[0]['e'])
        sw = parse_location(args[0]['s'], args[0]['w'])
    else:
        ne = LocationTuple(args[0])
        sw = LocationTuple(args[1])

    return BboxTuple(ne, sw)


def get_owm_zoom(zoom):
    for zrange, data in OWM_ZOOM.items():
        if zrange[0] <= int(zoom) <= zrange[1]:
            return data
    raise Exception('invalid "zoom" param')


def get_coords_range(points, p1, p2):
    pfrom = bisect.bisect_left(points, p1)
    pto = bisect.bisect_right(points, p2)
    return points[pfrom-1:pto+1]


def get_bbox_geohashes(ll_ne, ll_sw, owm_zoom):
    lats = get_coords_range(owm_zoom['lats'], ll_sw.lat, ll_ne.lat)
    lngs = get_coords_range(owm_zoom['lngs'], ll_sw.lng, ll_ne.lng)
    locations = product(lats, lngs, [owm_zoom['hash_precision']])

    return [geohash.encode(*ll) for ll in locations]


def get_bbox_area_grid(ll_ne, ll_sw, owm_zoom):
    hashes = get_bbox_geohashes(ll_ne, ll_sw, owm_zoom)
    bboxs = map(geohash.bbox, hashes)
    return [g for g in zip(hashes, map(parse_bbox, bboxs))]


if __name__ == '__main__':
    ll_ne = parse_location(50, 50)
    ll_sw = parse_location(-50, -50)
    print(get_bbox_area_grid(ll_ne, ll_sw, 9))
