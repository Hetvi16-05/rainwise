import os
import subprocess
import sys
import time
from datetime import datetime

# ----------------------
# paths
# ----------------------
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

PYTHON = "/Applications/miniconda3/bin/python"

LOCK_FILE = os.path.join(BASE_DIR, "pipeline.lock")
LAST_RUN_FILE = os.path.join(BASE_DIR, "pipeline_last_run.txt")


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
        print(f"[{datetime.now()}] 🚀 Running: {name}")

        result = subprocess.run(
            [PYTHON, path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ Failed: {name}")
            print(result.stderr)
            return False

        print(f"✅ Completed: {name}")
        return True

    except Exception as e:
        print(f"❌ Error in {name}: {e}")
        return False


# ----------------------
# pipeline
# ----------------------
def run_pipeline():

    if not run_script(
        "data_collection/realtime_weather.py",
        "Weather"
    ):
        return False

    if not run_script(
        "data_collection/realtime_rainfall.py",
        "Rainfall"
    ):
        return False

    if not run_script(
        "data_collection/realtime_river.py",
        "River"
    ):
        return False

    if not run_script(
        "data_collection/build_dataset.py",
        "Dataset"
    ):
        return False

    print("🎉 Pipeline completed successfully")
    return True


# ----------------------
# lock system (VERY IMPORTANT)
# ----------------------
def create_lock():

    if os.path.exists(LOCK_FILE):
        print("⚠️ Pipeline already running. Exiting.")
        sys.exit()

    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))


def remove_lock():

    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)


# ----------------------
# track last run
# ----------------------
def update_last_run():

    with open(LAST_RUN_FILE, "w") as f:
        f.write(str(datetime.now()))


# ----------------------
# main loop
# ----------------------
if __name__ == "__main__":

    print("🔥 Realtime pipeline started")

    create_lock()

    try:

        while True:

            interval = get_interval()

            print(
                f"\n📅 Month: {datetime.now().month} | ⏱ Interval: {interval} sec"
            )

            success = run_pipeline()

            if success:
                update_last_run()

            print(f"😴 Sleeping for {interval} seconds...\n")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("🛑 Stopped manually")

    finally:
        remove_lock()