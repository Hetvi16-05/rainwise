import pandas as pd
import numpy as np
import os

INPUT = "data/processed/training_dataset_gujarat_labeled.csv"
OUT_DIR = "data/bigdata"

COPIES = 125   # change later to 180 for 50GB

CHUNK = 100000

os.makedirs(OUT_DIR, exist_ok=True)

print("START")

for i in range(COPIES):

    print("Part", i)

    out_file = f"{OUT_DIR}/part_{i:03d}.csv"

    first = True

    for chunk in pd.read_csv(INPUT, chunksize=CHUNK):

        chunk["rain_mm"] += np.random.normal(0, 2, len(chunk))
        chunk["precip_mm"] += np.random.normal(0, 2, len(chunk))
        chunk["rain3_mm"] += np.random.normal(0, 1, len(chunk))
        chunk["rain7_mm"] += np.random.normal(0, 1, len(chunk))

        chunk["lat"] += np.random.uniform(-0.05, 0.05, len(chunk))
        chunk["lon"] += np.random.uniform(-0.05, 0.05, len(chunk))

        chunk.to_csv(
            out_file,
            mode="w" if first else "a",
            header=first,
            index=False
        )

        first = False

print("DONE")
