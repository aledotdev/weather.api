function initWeatherExplorer() {

  map.addListener('idle', function() {
    var bounds = map.getBounds();
    var zoom = map.getZoom();
    var ll_ne = bounds.getNorthEast().toUrlValue();
    var ll_sw = bounds.getSouthWest().toUrlValue();

    removeMarkers();

    getWeatherByBBox(ll_ne, ll_sw, zoom)
      .done(function(data) {
        for(var i in data) {
          addWeatherMarker(data[i]);
        }
      });
  });
}


function getWeatherByBBox(ll_ne, ll_sw, zoom) {
  var url = '/api/v1/weather/current/?';
  var url = url + 'll_ne=' + ll_ne + '&ll_sw=' + ll_sw + '&zoom=' + zoom;
  return $.get(url);
}

function addWeatherMarker(station) {
  var ll = new google.maps.LatLng(station.location[0], station.location[1]);

  var marker = new google.maps.Marker({
    position: ll,
    map: map,
    title: station.weather.title + ' / ' + station.weather.temperature.current + '°',
    icon: station.weather.icon
  });

  station_markers.push(marker);

}

function removeMarkers(){
  for(var i=0; i< station_markers.length; i++){
    station_markers[i].setMap(null);
  }
}
