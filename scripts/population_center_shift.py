import geopandas as gpd
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from shapely.geometry import LineString 





# Calculate population-weighted center
def calculate_population_center(gdf, year):
    gdf["centroid"] = gdf.geometry.centroid
    gdf["x"] = gdf["centroid"].x
    gdf["y"] = gdf["centroid"].y

    weighted_x = (
    (gdf["x"] * gdf["population"]).sum()
    / gdf["population"].sum()
    )

    weighted_y = (
    (gdf["y"] * gdf["population"]).sum()
    / gdf["population"].sum()
    )

    return{
        "year": year,
        "x": weighted_x,
        "y": weighted_y
    }



# Create point geodataframe from population centers
def create_pop_center_dataframe(population_centers):
    center_df = pd.DataFrame(population_centers)
    center_gdf = gpd.GeoDataFrame(
        center_df,
        geometry=gpd.points_from_xy(center_df["x"], center_df["y"]),
        crs="EPSG:26911"
    )
    return center_gdf


# Create population center shift line
def create_line_dataframe(center_gdf):
    movement_line = LineString(center_gdf.geometry.tolist())
    movement_gdf = gpd.GeoDataFrame(
        geometry=[movement_line],
        crs=center_gdf.crs
    )
    return movement_gdf 



# Map population in tracts
def map_population_centers(center_gdf, movement_gdf):
    fig, ax = plt.subplots(figsize=(10, 10))

    center_gdf.plot(
        ax=ax,
        color="blue",
        markersize=60
    )

    for x, y, label in zip(
        center_gdf.geometry.x,
        center_gdf.geometry.y,
        center_gdf["year"]
    ):
        ax.text(x+2, y+12, str(label))
    
    movement_gdf.plot(
        ax=ax,
        color="red",
        linewidth=1
    )

    plt.title(f"Kootenai County Population Center Shift")
    plt.savefig(
        "../results/population_center_shift.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.show()


# Measure shift distance of population centers
def measure_shift_distance(center_gdf):
    center_gdf["distance_from_previous_m"] = (
        center_gdf.geometry.distance(center_gdf.geometry.shift())
    )
    center_gdf["distance_km"] = (
        center_gdf["distance_from_previous_m"] / 1000
    )
    print(center_gdf[["year", "distance_km"]])
    # Save results
    center_gdf[["year", "distance_from_previous_m", "distance_km"]].to_csv(
        "../results/population_center_shift_distance.csv",
        index=False
    )

    return center_gdf


years = [2000, 2010, 2015, 2020, 2024]

gdfs = {}
population_centers = []

for year in years:
    shp_path = Path(f"../data/processed/population_tracts_{year}.shp")
    gdf = gpd.read_file(shp_path)
    gdfs[year] = gdf
    

    result = calculate_population_center(gdf, year)
    population_centers.append(result)

center_gdf = create_pop_center_dataframe(population_centers)
movement_gdf = create_line_dataframe(center_gdf)
map_population_centers(center_gdf, movement_gdf)

# Measure shift distance of population centers from year to year
center_gdf = measure_shift_distance(center_gdf)








