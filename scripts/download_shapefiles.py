import requests
from pathlib import Path
import zipfile
import geopandas as gpd 
import matplotlib.pyplot as plt
import pandas as pd 


pop_df = pd.read_csv(
    "../data/raw/kootenai_tract_population_2000_2024.csv"
)
pop_df["GEOID"] = pop_df["GEOID"].astype(str).str.zfill(11)


# Download census tract data 
def download_shapefile(year, zip_path):
    print(f"Downloading {year} ...")
    url = urls[year]
    r = requests.get(url)

    if r.status_code == 200:
        with open(zip_path, "wb") as f:
            f.write(r.content)
        print(f"{year} downloaded successfully")
    else:
        print(f"{year} FAILED: {r.status_code}")



# Extract census tract data
def extract_shapefile(year, extract_path, zip_path):
    print(f"Extracting {year}...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    print(f"{year} extracted successfully")


# Read shapefile
def find_read_shapefil(year, extract_path):
    print(f"Reading Shapefile for {year}...")
    shp_file = list(extract_path.glob("*.shp"))[0]
    gdf = gpd.read_file(shp_file)
    print(f"Shapefile: {year} loaded successfully")
    return gdf 


# Filter county (Kootenai)
def filter_county(gdf):
    print(gdf.columns)
    if "COUNTYFP" in gdf.columns:
        gdf = gdf[gdf["COUNTYFP"] == "055"]
    elif "COUNTY" in gdf.columns:
        gdf = gdf[gdf["COUNTY"] == "055"]
    return gdf 



# Create GEOID if it does not exist
# with state, county and tract
def create_geoid(gdf):
    if "GEOID" not in gdf.columns: 
        if "STATEFP" in gdf.columns:
            state = gdf["STATEFP"].astype(str).str.zfill(2)
        else:
            state = gdf["STATE"].astype(str).str.zfill(2)

        if "COUNTYFP" in gdf.columns:
            county = gdf["COUNTYFP"].astype(str).str.zfill(3)
        else:
            county = gdf["COUNTY"].astype(str).str.zfill(3)

        if "TRACTCE" in gdf.columns:
            tract = gdf["TRACTCE"].astype(str).str.zfill(6)
        else:
            tract = gdf["TRACT"].astype(str).str.zfill(6)

        gdf["GEOID"] = state + county + tract
    
    # standardize final format
    gdf["GEOID"] = gdf["GEOID"].astype(str).str.zfill(11)

    return gdf


# Convert coordinate system
def convert_coordinate(gdf):
    print(f"before coordinate: {gdf.crs}")
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4269)

    gdf = gdf.to_crs(epsg=26911) # NAD83 / UTM Zone 11N    
    print(f"after coordinate: {gdf.crs}")
    return gdf 


# Set Up Dirctory
raw_dir = Path("../data/raw")
zip_dir = raw_dir / "zipped"
extract_dir = raw_dir / "extracted"

zip_dir.mkdir(parents=True, exist_ok=True)
extract_dir.mkdir(parents=True, exist_ok=True)


# Download and Extract
years = [2000, 2010, 2015, 2020, 2024]
urls = {
    2000: "https://www2.census.gov/geo/tiger/PREVGENZ/tr/tr00shp/tr16_d00_shp.zip",
    2010: "https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_16_140_00_500k.zip",
    2015: "https://www2.census.gov/geo/tiger/GENZ2015/shp/cb_2015_16_tract_500k.zip",
    2020: "https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_16_tract_500k.zip",
    2024: "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_16_tract_500k.zip",
}

# data and dataframes
gdfs = {}
population_centers = []

for year in years: 
    zip_path = zip_dir / f"tract_{year}.zip"
    extract_path = extract_dir / f"tract_{year}"
    extract_path.mkdir(parents=True, exist_ok=True)

    #download_shapefile(year, zip_path)
    #extract_shapefile(year, extract_path, zip_path)
    

    # Read Shapefiles
    gdf = find_read_shapefil(year, extract_path)


    # Filter Kootenai County
    gdf = filter_county(gdf)
    print(gdf.head( ))
    
    # Create GEOID 
    gdf = create_geoid(gdf)
    print(gdf["GEOID"].head())
    print(gdf["GEOID"].str.len().unique())
    
    # Add year label to gdf
    gdf["year"] = year


    # Convert coordinate system
    gdf = convert_coordinate(gdf)

    # Join 2 dataframes 
    pop_year = pop_df[pop_df["year"] == year]

    gdf = gdf.merge(
        pop_year[["GEOID", "population"]],
        on="GEOID",
        how="left"
    )

    missing_pop = gdf["population"].isna().sum()
    print(f"{year} missing population tracts: {missing_pop}")
    print(gdf[gdf["population"].isna()][["GEOID"]])

    gdfs[year] = gdf
    print(f"{year} ready: {len(gdf)} tracts")
    print(gdf[["GEOID", "population"]].head())
    
    #gdf.plot()
    #plt.show()

    output_path = Path(f"../data/processed/population_tracts_{year}.shp")
    gdf.to_file(output_path)

    


