import geopandas as gpd
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path


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


# Calculate population ranges
def calculate_population_ranges(gdfs):
    yearly_ranges = {}
    global_min = float("inf")
    global_max = float("-inf")

    # Calculate yearly ranges
    for year, gdf in gdfs.items():
        year_min = gdf["population"].min()
        year_max = gdf["population"].max()
        total_pop = gdf["population"].sum()

        yearly_ranges[year] = {
            "year": year,
            "min_population": year_min,
            "max_population": year_max,
            "total_population": total_pop
        }

        print(
            f"{year}: min={year_min}, max={year_max}, "
            f"total={total_pop}"
        )

        # Update global range
        global_min = min(global_min, year_min)
        global_max = max(global_max, year_max)

    print("\nGLOBAL RANGE")
    print(f"min={global_min}, max={global_max}")

    # Convert to dataframe
    range_df = pd.DataFrame(yearly_ranges.values())

    # Add global range row
    global_row = pd.DataFrame([{
        "year": "GLOBAL",
        "min_population": global_min,
        "max_population": global_max
    }])

    range_df = pd.concat(
        [range_df, global_row],
        ignore_index=True
    )

    # Save results
    output_path = Path("../results/population_ranges.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    range_df.to_csv(output_path, index=False)

    print("\nPopulation ranges saved!")
    return (yearly_ranges, global_min, global_max)


# Create equal interval bins
def create_bins(global_min, global_max):

    interval = (global_max - global_min) / 5
    bins = [
        global_min,
        global_min + interval,
        global_min + interval * 2,
        global_min + interval * 3,
        global_min + interval * 4,
        global_max
    ]
    print("\nCLASS BREAKS")
    print(bins)
    return bins


# Map population in tracts
def map_population(gdf, center_gdf, year, bins):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_axis_off()
    gdf.plot(
        column="population",
        cmap="OrRd",
        legend=True,
        scheme="UserDefined",
        classification_kwds={"bins": bins[1:-1]},
        legend_kwds={"title": "Population", "fontsize": 9},
        edgecolor="gray",
        linewidth=0.6,
        ax=ax
    )

    center_year = center_gdf[center_gdf["year"] == year]
    center_year.plot(
        ax=ax,
        color="black",
        markersize=80,
        edgecolor="white",
        linewidth=0.5
    )

    plt.title(
        f"Population Distribution — Kootenai County ({year})",
        fontsize=14,
        fontweight="bold"
    )
    plt.tight_layout()

    output_path = Path(f"../results/figures/population_tract_{year}.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


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

yearly_ranges, global_min, global_max = (calculate_population_ranges(gdfs))

bins = create_bins(global_min, global_max)

for year in years:
    gdf = gdfs[year]
    map_population(gdf, center_gdf, year, bins)

# Animation creation 
# folder containing saved maps
image_dir = Path("../results/figures")

# ordered image list
years = [2000, 2010, 2015, 2020, 2024]
images = []

for year in years:
    img_path = image_dir / f"population_tract_{year}.png"
    img = Image.open(img_path)
    images.append(img)

# save GIF
gif_path = image_dir / "population_shift_animation.gif"
images[0].save(
    gif_path,
    save_all=True,
    append_images=images[1:],
    duration=2000,   # milliseconds per frame
    loop=0
)
print("GIF animation saved!")





