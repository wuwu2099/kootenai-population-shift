import geopandas as gpd
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from shapely.geometry import LineString


# Population-weighted center
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

    return {
        "year": year,
        "x": weighted_x,
        "y": weighted_y
    }



# Build center GeoDataFrame
def create_pop_center_dataframe(population_centers):
    df = pd.DataFrame(population_centers)
    df = df.sort_values("year")  # IMPORTANT
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["x"], df["y"]),
        crs="EPSG:26911"
    )
    return gdf



# Create movement line
def create_line_dataframe(center_gdf):
    coords = list(zip(center_gdf.geometry.x, center_gdf.geometry.y))
    line = LineString(coords)
    movement_gdf = gpd.GeoDataFrame(
        geometry=[line],
        crs=center_gdf.crs
    )
    return movement_gdf



# Map visualization
def map_population_centers(center_gdf, movement_gdf):
    fig, ax = plt.subplots(figsize=(10, 10))
    #ax.set_axis_off()

    # Movement path
    movement_gdf.plot(
        ax=ax,
        color="red",
        linewidth=2,
        alpha=0.8
    )
    # Center points
    center_gdf.plot(
        ax=ax,
        color="black",
        markersize=90,
        edgecolor="white",
        linewidth=0.8
    )
    # Labels
    for x, y, year in zip(
        center_gdf.geometry.x,
        center_gdf.geometry.y,
        center_gdf["year"]
    ):
        ax.text(
            x,
            y + 12,
            str(year),
            fontsize=10,
            fontweight="bold"
        )
    # Title
    plt.title(
        "Population Center Shift — Kootenai County (2000–2024)",
        fontsize=15,
        fontweight="bold"
    )
    # Save
    output_path = Path("../results/population_center_shift.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )
    plt.show()


# Distance calculation
def measure_shift_distance(center_gdf):
    center_gdf = center_gdf.sort_values("year").reset_index(drop=True)
    center_gdf["distance_from_previous_m"] = (
        center_gdf.geometry.distance(
            center_gdf.geometry.shift()
        )
    )
    center_gdf["distance_km"] = (center_gdf["distance_from_previous_m"] / 1000)
    print(center_gdf[["year", "distance_km"]])

    output_path = Path("../results/population_center_shift_distance.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    center_gdf[[
        "year",
        "distance_from_previous_m",
        "distance_km"
    ]].to_csv(output_path, index=False)
    return center_gdf


# MAIN WORKFLOW
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
center_gdf = measure_shift_distance(center_gdf)








