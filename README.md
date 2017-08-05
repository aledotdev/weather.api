Fetchs data from Open Weather Map (OWM) API using bounding boxes.
The idea is has a service to display weather data in a map in real time.
This service fetchs data from the OWM API and stores it in cache to reduce the calls to OWM.

It uses Geohash to build a grid to organize de weather data.
- https://en.wikipedia.org/wiki/Geohash
- http://geohash.gofreerange.com/

### Api call example:
[http://localhost:8000/api/v1/weather/current/?ll_ne=-31.344059,%20-64.056702&ll_sw=-31.489773,%20-74.307213&zoom=15](http://localhost:8000/api/v1/weather/current/?ll_ne=-31.344059,%20-64.056702&ll_sw=-31.489773,%20-74.307213&zoom=15)
```
ll_ne=-31.344059,-64.056702 // Nort East point
ll_sw=-31.489773,-74.307213 // South West Point
zoom=15 // Zoom
```

### How to install

- This code runs under Python 3
- You needs redis to cache
- Clone the repository
- Create a file `weatherapi/settings/local.py`
- Set your OWM api key: `OWM_API_KEY`
- run `# python run.py`
- You can try navigate on google maps: `http://localhost:8000/map`

### Esp:

La idea es tener una API que obtenga datos del tiempo del servicio de open weather map (OWM) para mostrar sobre un mapa.

Como parametro le paso un bounding box (bbox, un area) y me devuelve el estado de todas las estaciones de clima que encuentre en ese area.
Para definir el bbox le paso las coordenada SW (sur-oeste) y la coordenada NE (nor-este)

OWM tiene un endpoint donde puedo obtener los datos dentro de un bbox que le paso como parametro.
Ademas de bbox tambien recibe como parametro el zoom el cual me define la densidad de estaciones que va a mostrar.
Hay 3 niveles de zoom Pais->estado->ciudad (por poner un nombre)

Basicamente este servicio es como un proxy de OWM donde podemos cachear las llamadas y controlar el uso del servicio  de OWM.

Para cachear las llamadas a OWM se utiliza una grilla. Hay una grilla por cada nivel de zoom.
Para generar las grillas usamos Geohash (https://en.wikipedia.org/wiki/Geohash) y cada nivel de zoom corresponde a un nivel de precision de Geohash.
