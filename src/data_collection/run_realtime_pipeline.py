import os
import subprocess
import sys
import time
from datetime import datetime

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

PYTHON = "/Applications/miniconda3/bin/python"


# ----------------------
# interval rule India monsoon
# ----------------------
def get_interval():

    month = datetime.now().month

    if month in [6, 7, 8, 9, 10]:
        return 600   # 10 min

    return 3600  # 60 min


# ----------------------
# run script safely
# ----------------------
def run_script(script, name):

    path = os.path.join(BASE_DIR, script)

    try:

        print(f"[{datetime.now()}] {name}")

        subprocess.run(
            [PYTHON, path],
            check=True
        )

    except Exception as e:

        print("Error:", name, e)


# ----------------------
# pipeline
# ----------------------
def run_pipeline():

    run_script(
        "data_collection/realtime_weather.py",
        "Weather"
    )

    run_script(
        "data_collection/realtime_rainfall.py",
        "Rainfall"
    )

    run_script(
        "data_collection/realtime_river.py",
        "River"
    )

    run_script(
        "data_collection/build_dataset.py",
        "Dataset"
    )

    print("Done")


# ----------------------
# main loop
# ----------------------
if __name__ == "__main__":

    print("Realtime pipeline started")

    while True:

        interval = get_interval()

        print(
            "Month:",
            datetime.now().month,
            "Interval:",
            interval
        )

        run_pipeline()

        time.sleep(interval)
