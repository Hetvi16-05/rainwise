import pandas as pd
from pathlib import Path
import os

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

WEATHER = os.path.join(
    BASE_DIR,
    "data/raw/realtime/weather/realtime_weather_log.csv"
)

RAIN = os.path.join(
    BASE_DIR,
    "data/raw/realtime/rainfall/realtime_rainfall_log.csv"
)

RIVER = os.path.join(
    BASE_DIR,
    "data/raw/realtime/river/realtime_river_level_log.csv"
)

FEATURES = os.path.join(
    BASE_DIR,
    "data/processed/features/final_features.csv"
)

OUT = os.path.join(
    BASE_DIR,
    "data/processed/realtime_dataset.csv"
)

Path(os.path.dirname(OUT)).mkdir(parents=True, exist_ok=True)


def latest(df):
    df = df.sort_values(df.columns[0])
    return df.groupby("city").tail(1)


weather = latest(pd.read_csv(WEATHER))
rain = latest(pd.read_csv(RAIN))
river = latest(pd.read_csv(RIVER))


df = weather.merge(
    rain,
    on=["city", "lat", "lon"],
    how="left",
)

df = df.merge(
    river,
    on=["city", "lat", "lon"],
    how="left",
)


try:

    feat = pd.read_csv(FEATURES)

    feat = feat.head(len(df))

    df = pd.concat(
        [df.reset_index(drop=True), feat],
        axis=1
    )

except Exception as e:

    print("No features", e)


df.to_csv(OUT, index=False)

print("Saved:", OUT)