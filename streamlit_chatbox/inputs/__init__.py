import streamlit.components.v1 as components
import difflib
from pathlib import Path
import re
import simplejson as json

__all__ = ['st_echarts', 'MAPS', 'CITY_CORRDS', 'JsCode', 'CustomMap']


ROOT_PATH = Path(__file__).parent.absolute()

_st_echarts = components.declare_component('st_echarts',
                                           path=ROOT_PATH.joinpath('frontend'))


def st_echarts(option,
               notMerge=False,
               lazyUpdate=False,
               theme='white',
               renderer='canvas',
               width=600,
               height=400,
               # extra_js=[],
               extra_maps=[],
               events={},
               returnData=None,
               key=None):
    extra_js = set()
    maps = set()

    geo = option.get('geo', {})
    if geo:
        map = geo.get('map')
        if map:
            maps.add(map)

    series = option.get('series', [])
    for s in series:
        map = s.get('mapType')
        if map:
            maps.add(map)

        type_=s.get('type','')

        if type_=='wordClound':
        	extra_js.add('echarts-wordcloud.min.js')
        elif type_=='liquidFill':
        	extra_js.add('echarts-liquidfill.min.js')
        elif type_.endswith('3D'):
        	extra_js.add('echarts-gl.min.js')
        # todo: support mapglobe/options

    if maps:
        MAPS.load_data()

    extra_js = list(extra_js | set([MAPS[x] for x in maps]))

    # if theme:
    # 	extra_js.append('themes/{}.js'.format(theme))

    if not isinstance(extra_maps, list):
        extra_maps = [extra_maps]

    return _st_echarts(option=option,
                       notMerge=notMerge,
                       lazyUpdate=lazyUpdate,
                       theme=theme,
                       renderer=renderer,
                       width=width,
                       height=height,
                       extra_js=extra_js,
                       extra_maps=extra_maps,
                       events=events,
                       returnData=returnData,
                       key=key)


def _get_close_matches(*args, **kw):
    return difflib.get_close_matches(*args, **kw)[0]


def _is_english(text):
    return bool(re.match(r'^[a-zA-Z0-9\s\-_]+$', text))


def JsCode(js):
    return '{p} {js} {p}'.format(p='--x_x--0_0--', js=js)


def CustomMap(self, map_name, geo_json, special_areas=None):
    return {
        'mapName': map_name,
        'geoJSON': geo_json,
        'specialAreas': special_areas,
    }


class CityCoords:
    _ins = None

    def __new__(cls):
        if cls._ins is None:
            cls._ins = super().__new__(cls)
        return cls._ins

    def __init__(self):
        self.data = {}

    def load_data(self, refresh=False):
        if not self.data or refresh:
            with ROOT_PATH.joinpath('frontend', 'data', 'city_coordinates.json').open(encoding = 'utf-8') as fp:
                self.data.update(json.load(fp))
        return self

    def __getitem__(self, key):
        key = _get_close_matches(key, self.data.keys())
        return key, self.data[key]

    def __setitem__(self, key, val):
        self.data[key] = val

    def update(self, d={}, **kw):
        self.data.update(d, **kw)


class Maps:
    _ins = None

    def __new__(cls):
        if cls._ins is None:
            cls._ins = super().__new__(cls)
        return cls._ins

    def __init__(self):
        self.cn = {}
        self.en = {}

    def load_data(self, refresh=False):
        if not self.cn or refresh:
            with ROOT_PATH.joinpath('frontend', 'data', 'map_filename.json').open(encoding = 'utf-8') as fp:
                for k, v in json.load(fp).items():
                    if v[0].startswith('maps/'):
                        en = v[0].replace('maps/', '')
                        map = v[0]+'.'+v[1]
                        en = re.sub(r'[\d_]+', ' ', en).strip()
                        self.cn[k] = map
                        self.en[en] = map
        return self

    def __getitem__(self, key):
        if _is_english(key):
            key = _get_close_matches(key, self.en.keys())
            return self.en.__getitem__(key)
        else:
            key = _get_close_matches(key, self.cn.keys())
            return self.cn.__getitem__(key)


CITY_CORRDS = CityCoords()
MAPS = Maps()

if __name__ == '__main__':
    import streamlit as st

    st.markdown(Path(__file__).parent.parent.absolute().joinpath(
        'README.md').read_text())
