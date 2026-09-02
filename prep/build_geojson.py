#Libraries
import pandas as pd
import geopandas as gpd
import osmnx as ox

############## Import travel data stored on Google Sheets ##############
trips = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vRb5sfrac1v5ltBRyZWFVk4hXUY5R1chhrmd6eZEXOr-TH9nErYvcPLAI8AKzD6S23PE1NX_KIIlYz2/pub?gid=0&single=true&output=csv")
visited_country_names = trips["Country"].dropna().unique().tolist()
visited_provinces = trips[trips["Type"] == "Province"][["City/Province", "Country"]].dropna().values.tolist()
visited_cities = trips[trips["Type"] == "City"][["City/Province", "Country"]].dropna().values.tolist()

############## Load city and province data ##############
gpkg_path = "data/natural_earth_vector.gpkg"
countries = gpd.read_file(gpkg_path, layer="ne_10m_admin_0_countries")
provinces = gpd.read_file(gpkg_path, layer="ne_10m_admin_1_states_provinces")

############## Filter countries and columns ##############
columns_to_keep = ["NAME", "ISO_A2", "ISO_A3", "geometry"]
countries_trimmed = countries[columns_to_keep]
countries_visited = countries_trimmed[countries_trimmed["NAME"].isin(visited_country_names)]
countries_visited.to_file("data/countries.geojson", driver="GeoJSON")
print(f"Countries: {len(countries_visited)}")

############### Filter provinces and columns ##############
columns_to_keep = ["name_en", "admin", "iso_a2", "geometry"]  
all_provinces_trimmed = provinces[columns_to_keep]
visited_province_names = [p[0] for p in visited_provinces]
visited_country_for_province = [p[1] for p in visited_provinces]
provinces_visited = all_provinces_trimmed[
    all_provinces_trimmed.apply(lambda row: [row["name_en"], row["admin"]] in visited_provinces, axis=1)
]

provinces_visited.to_file("data/provinces.geojson", driver="GeoJSON")
print(f"Provinces: {len(provinces_visited)}")

#Sanity check
print(f"Countries: {len(countries_visited)} / expected {len(set(visited_country_names))}")
print(f"Provinces: {len(provinces_visited)} / expected {len(set(visited_province_names))}")

############## Filter cities and columns ##############
city_names = [f"{city}, {country}" for city, country in visited_cities]
city_boundaries = []
#Get boundaries of each city
for name in city_names:
    boundary = ox.geocode_to_gdf(name)
    city_boundaries.append(boundary)
cities_gdf = pd.concat(city_boundaries, ignore_index=True)
cities_gdf = gpd.GeoDataFrame(cities_gdf, geometry="geometry", crs="EPSG:4326")

# Use the centre of the city to determine if found in a province already mentioned (Drop if so)
cities_points = cities_gdf.copy()
cities_points_metric = cities_points.to_crs(cities_points.estimate_utm_crs())
cities_points["geometry"] = cities_points_metric.centroid
cities_points = cities_points.to_crs("EPSG:4326")
cities_with_province = gpd.sjoin(
    cities_points,
    provinces_visited[["name_en", "admin", "geometry"]],
    predicate="within"
)
names_to_keep = cities_with_province[~cities_with_province["name_en"].isin(visited_province_names)]["name"]
unmatched = set(cities_gdf["name"]) - set(cities_with_province["name"])
names_to_keep = list(names_to_keep) + list(unmatched)
cities_trimmed = cities_gdf[cities_gdf["name"].isin(names_to_keep)][["display_name", "geometry"]]
cities_trimmed.to_file("data/cities.geojson", driver="GeoJSON")
print(f"Cities: {len(cities_trimmed)}")