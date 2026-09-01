#Libraries
import geopandas as gpd
import fiona
import osmnx as ox
import pandas as pd

'''
# list all layers inside the geopackage
layers = fiona.listlayers("data/natural_earth_vector.gpkg")
print(layers)'''

#Load data
gpkg_path = "data/natural_earth_vector.gpkg"
countries = gpd.read_file(gpkg_path, layer="ne_10m_admin_0_countries")
provinces = gpd.read_file(gpkg_path, layer="ne_10m_admin_1_states_provinces")

###Temporary list (Find a better way)
visited_country_names = ["Germany", "France", "Japan"]  
visited_provinces = [
    ("Bavaria", "Germany"),
    ("Sichuan", "China"),
]

#Filter countries and columns
columns_to_keep = ["NAME", "ISO_A2", "ISO_A3", "geometry"]
countries_trimmed = countries[columns_to_keep]
countries_visited = countries_trimmed[countries_trimmed["NAME"].isin(visited_country_names)]
countries_visited.to_file("data/countries.geojson", driver="GeoJSON")

#Filter provinces and columns
columns_to_keep = ["name_en", "admin", "iso_a2", "geometry"]  
provinces_trimmed = provinces[columns_to_keep]
visited_province_names = [p[0] for p in visited_provinces]
visited_country_for_province = [p[1] for p in visited_provinces]

provinces_visited = provinces_trimmed[
    provinces_trimmed.apply(lambda row: (row["name_en"], row["admin"]) in visited_provinces, axis=1)
]
provinces_visited.to_file("data/provinces.geojson", driver="GeoJSON")

#Sanity check
print(f"Countries: {len(countries_visited)} / expected {len(set(visited_country_names))}")
print(f"Provinces: {len(provinces_visited)} / expected {len(set(visited_province_names))}")

############## Cities ##############
city_names = ["Munich, Germany", "Chengdu, China"]

city_boundaries = []
for name in city_names:
    boundary = ox.geocode_to_gdf(name)
    city_boundaries.append(boundary)

cities_gdf = pd.concat(city_boundaries, ignore_index=True)
cities_gdf = gpd.GeoDataFrame(cities_gdf, geometry="geometry", crs="EPSG:4326")
cities_trimmed = cities_gdf[["display_name", "geometry"]]
cities_trimmed.to_file("data/cities.geojson", driver="GeoJSON")
import matplotlib.pyplot as plt
boundary = ox.geocode_to_gdf("Munich, Germany")
print(boundary)
print(boundary.geom_type)
boundary.plot()
plt.show()