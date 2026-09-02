const map = new maplibregl.Map({
  container: 'map',
  style: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
  center: [0, 20],
  zoom: 1
});

/************************ Stats *************************/
fetch('data/stats.json')
  .then(response => response.json())
  .then(stats => {
    document.getElementById('stats').innerHTML = `
      <p>🌍 ${stats.countries} countries &nbsp; 🏙️ ${stats.cities} cities &nbsp; 🏞️ ${stats.provinces} provinces</p>
    `;
  })
  .catch(err => console.error('Failed to load stats:', err));

/************************ Map *************************/
map.on('load', () => {
  // --- Countries layer ---
  map.addSource('countries', {
    type: 'geojson',
    data: 'data/countries.geojson'
  });
  map.addLayer({
    id: 'countries-outline',
    type: 'line',
    source: 'countries',
    paint: {
      'line-color': '#ff6b35',
      'line-width': 2
    }
  });

  // --- Provinces layer ---
  map.addSource('provinces', {
    type: 'geojson',
    data: 'data/provinces.geojson'
  });
  map.addLayer({
    id: 'provinces-fill',
    type: 'fill',
    source: 'provinces',
    paint: {
      'fill-color': '#3388ff',
      'fill-opacity': 0.2
    }
  });
  map.addLayer({
    id: 'provinces-outline',
    type: 'line',
    source: 'provinces',
    paint: {
      'line-color': '#3388ff',
      'line-width': 1.5
    }
  });

  // --- Cities layer ---
  map.addSource('cities', {
    type: 'geojson',
    data: 'data/cities.geojson'
  });
  map.addLayer({
    id: 'cities-fill',
    type: 'fill',
    source: 'cities',
    paint: {
      'fill-color': '#2ecc71',
      'fill-opacity': 0.3
    }
  });
  map.addLayer({
    id: 'cities-outline',
    type: 'line',
    source: 'cities',
    paint: {
      'line-color': '#2ecc71',
      'line-width': 1.5
    }
  });
    const countryLayers = ['countries-outline'];
    const detailLayers = ['provinces-fill', 'provinces-outline', 'cities-fill', 'cities-outline'];

    function setMode(mode) {
    const showCountries = mode === 'countries';

    countryLayers.forEach(id => {
        map.setLayoutProperty(id, 'visibility', showCountries ? 'visible' : 'none');
    });
    detailLayers.forEach(id => {
        map.setLayoutProperty(id, 'visibility', showCountries ? 'none' : 'visible');
    });

    document.getElementById('btn-countries').classList.toggle('active', showCountries);
    document.getElementById('btn-detail').classList.toggle('active', !showCountries);
    }

    document.getElementById('btn-countries').addEventListener('click', () => setMode('countries'));
    document.getElementById('btn-detail').addEventListener('click', () => setMode('detail'));

    setMode('countries'); // default view on load

    document.getElementById('btn-fullscreen').addEventListener('click', () => {
      const mapEl = document.getElementById('map');

      if (!document.fullscreenElement) {
        mapEl.requestFullscreen();
      } else {
        document.exitFullscreen();
      }
    });
});

