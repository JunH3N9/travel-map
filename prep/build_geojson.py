#Libraries
import pandas as pd
import geopandas as gpd
import osmnx as ox
import json

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
names_to_keep = set(list(names_to_keep) + list(unmatched))
cities_visited = cities_gdf[cities_gdf["name"].isin(names_to_keep)][["display_name", "geometry"]]
cities_visited.to_file("data/cities.geojson", driver="GeoJSON")

#Sanity check
'''
print(f"Countries: {len(countries_visited)} / expected {len(set(visited_country_names))}")
print(f"Provinces: {len(provinces_visited)} / expected {len(set(visited_province_names))}")
print(f"Cities: {len(cities_visited)} / expected {len(set(city_names))}")'''


############## Stats ##############
stats_df = pd.DataFrame(
    columns=["country", "flag", "city_province", "country_area", "travelled_area", "travelled_area_percentage"]
    )
stats_df["country"] = countries_visited["NAME"]
#Flag emoji
'''def country_code_to_flag(iso_code):
    return "".join(chr(ord(c) + 127397) for c in iso_code.upper())'''
stats_df["flag"] = countries_visited["ISO_A2"]

for country in stats_df["country"]:
    country_area = countries_visited[countries_visited["NAME"] == country].to_crs("EPSG:6933").geometry.area.values[0] / 1_000_000
    travelled_area = provinces_visited[provinces_visited["admin"] == country].to_crs("EPSG:6933").geometry.area.sum() / 1_000_000
    travelled_area += cities_visited[cities_visited["display_name"].str.contains(country)].to_crs("EPSG:6933").geometry.area.sum() / 1_000_000
    travelled_area_percentage = (travelled_area / country_area) * 100 if country_area > 0 else 0

    city_province_list = cities_visited[cities_visited["display_name"].str.contains(country)]["display_name"].tolist()
    for city in city_province_list:
        city_province_list[city_province_list.index(city)] = city.split(",")[0]
    city_province_list += provinces_visited[provinces_visited["admin"] == country]["name_en"].tolist()
    city_province_list = ", ".join(city_province_list)

    stats_df.loc[stats_df["country"] == country, "country_area"] = country_area
    stats_df.loc[stats_df["country"] == country, "travelled_area"] = travelled_area
    stats_df.loc[stats_df["country"] == country, "travelled_area_percentage"] = travelled_area_percentage
    stats_df.loc[stats_df["country"] == country, "city_province"] = city_province_list
print(stats_df)

with open("data/stats.json", "w") as f:
    json.dump(stats_df.to_dict(orient="records"), f)