import requests
import pandas as pd

STATE = "16"
COUNTY = "055"
API_KEY = "your_api_key"  



def fetch_to_df(url, year, source, value_col, api_key=None):
    if api_key:
        separator = "&" if "?" in url else "?"
        url += f"{separator}key={api_key}"

    r = requests.get(url)

    print(f"\n[{year}] STATUS:", r.status_code)

    if r.status_code != 200:
        print(r.text[:300])
        return None

    try:
        data = r.json()
    except Exception as e:
        print("JSON ERROR:", e)
        print(r.text[:300])
        return None

    df = pd.DataFrame(data[1:], columns=data[0])

    # create unique tract id
    df["GEOID"] = (
    df["state"].astype(str).str.zfill(2)
    + df["county"].astype(str).str.zfill(3)
    + df["tract"].astype(str).str.zfill(6)
    )

    # standardize schema (IMPORTANT)
    df = df[["GEOID", "NAME", value_col, "state", "county", "tract"]]

    df = df.rename(columns={value_col: "population"})

    df["year"] = year
    df["source"] = source

    return df


# ----------------------------
# RAW DATA COLLECTION
# ----------------------------

dfs = []

# 2000
dfs.append(fetch_to_df(
    "https://api.census.gov/data/2000/dec/sf1"
    "?get=P001001,NAME"
    f"&for=tract:*&in=state:{STATE}%20county:{COUNTY}",
    2000, "dec_sf1", "P001001",
    API_KEY
))

# 2010
dfs.append(fetch_to_df(
    "https://api.census.gov/data/2010/dec/sf1"
    "?get=P001001,NAME"
    f"&for=tract:*&in=state:{STATE}%20county:{COUNTY}",
    2010, "dec_sf1", "P001001",
    API_KEY
))

# 2015 ACS
dfs.append(fetch_to_df(
    "https://api.census.gov/data/2015/acs/acs5"
    "?get=B01003_001E,NAME"
    f"&for=tract:*&in=state:{STATE}%20county:{COUNTY}",
    2015, "acs5_2015", "B01003_001E",
    API_KEY
))

# 2020
dfs.append(fetch_to_df(
    "https://api.census.gov/data/2020/dec/pl"
    "?get=P1_001N,NAME"
    f"&for=tract:*&in=state:{STATE}%20county:{COUNTY}",
    2020, "dec_pl", "P1_001N",
    API_KEY
))

# 2024 ACS
dfs.append(fetch_to_df(
    "https://api.census.gov/data/2024/acs/acs5"
    "?get=B01003_001E,NAME"
    f"&for=tract:*&in=state:{STATE}%20county:{COUNTY}",
    2024, "acs5", "B01003_001E", API_KEY
))


# ----------------------------
# FINAL RAW TABLE (NO MERGING)
# ----------------------------
df_raw = pd.concat([d for d in dfs if d is not None], ignore_index=True)

# convert population to numeric
df_raw["population"] = pd.to_numeric(df_raw["population"], errors="coerce")

# save
df_raw.to_csv("../data/raw/kootenai_tract_population_2000_2024.csv", index=False)

print("\nDONE ✔")
print(df_raw.head())