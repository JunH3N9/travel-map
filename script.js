const map = new maplibregl.Map({
  container: 'map',
  style: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
  center: [0, 20],
  zoom: 1
});

/************************ Stats *************************/
fetch('data/stats.json')
  .then(response => response.json())
  .then(data => {
    renderCountryList(data.countries);
    renderSummaryBox(data.summary);
  })
  .catch(err => console.error('Failed to load stats:', err));
    
function renderCountryList(countries) {
  const container = document.getElementById('country-list');
    const rows = countries.map(row => `
      <div style="margin-bottom: 20px;">
        <div style="display: flex; align-items: baseline; gap: 10px; margin-bottom: 6px;">
          <span class="fi fi-${row.flag.toLowerCase()}" style="font-size: 18px;"></span>
          <span style="font-size: 14px; font-weight: 500; flex: 1;">${row.country}</span>
          <span style="font-size: 13px; color: #888;">
            ${row.travelled_area_percentage.toFixed(2)}%
            (${Math.round(row.travelled_area).toLocaleString()} / ${Math.round(row.country_area).toLocaleString()} km²)
          </span>
        </div>
        <div style="height: 8px; background: #eee; border-radius: 4px; overflow: hidden;">
          <div style="height: 100%; width: ${row.travelled_area_percentage}%; background: #2a78d6; border-radius: 4px;"></div>
        </div>
        <div style="font-size: 13px; color: #888; margin-top: 6px;">${row.city_province}</div>
      </div>
    `).join('');

    container.innerHTML = rows;
  }
function renderSummaryBox(summary) {
  const container = document.getElementById('summary-box');
 
  // furthest_location is [name, distance_km, country]
  const [furthestName, furthestDistance, furthestCountry] = summary.furthest_location;
 
  container.innerHTML = `
    <div class="stat-card">
      <p class="stat-label">Countries</p>
      <p class="stat-value">${summary.total_countries}</p>
    </div>
    <div class="stat-card">
      <p class="stat-label">Continents</p>
      <p class="stat-value">${summary.total_continents}</p>
    </div>
    <div class="stat-card">
      <p class="stat-label">Provinces</p>
      <p class="stat-value">${summary.total_provinces}</p>
    </div>
    <div class="stat-card">
      <p class="stat-label">Cities</p>
      <p class="stat-value">${summary.total_cities}</p>
    </div>
    <div class="stat-card furthest">
      <p class="stat-label">Furthest Location</p>
      <p class="stat-value-sm">${furthestName}, ${furthestCountry}</p>
      <p class="stat-unit">${Math.round(furthestDistance).toLocaleString()} km from home</p>
    </div>
    <div class="stat-card area">
      <p class="stat-label">Total Area Traveled</p>
      <p class="stat-value">${Math.round(summary.total_area).toLocaleString()} km²</p>
    </div>
  `;
}  

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

