import time
from datetime import datetime
import json
import os

HISTORY_FILE = "execution_history.json"


def save_result(result):
    data = []

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)

    data.append(result)

    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def show_dashboard(result):
    print("\n" + "="*40)
    print("🚀 AUTOMATION DASHBOARD")
    print("="*40)

    print(f"Testcase     : {result['testcase']}")
    print(
        f"Status       : {'✅ PASSED' if result['status']=='Passed' else '❌ FAILED'}")
    print(f"Start Time   : {result['start_time']}")
    print(f"End Time     : {result['end_time']}")
    print(f"Duration     : {result['duration']} seconds")

    if result["status"] == "Not Passed":
        print("\n🧠 FAILURE ANALYSIS")
        print("-"*40)
        print(f"Error Type   : {result.get('type')}")
        print(f"Root Cause   : {result.get('root_cause')}")
        print(f"Category     : {result.get('category')}")
        print(f"Severity     : {result.get('severity')}")
        print(f"Suggested Fix: {result.get('solution')}")

    print("\n📊 SUMMARY")
    print("-"*40)

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)

        total = len(data)
        durations = [d["duration"] for d in data]

        avg_duration = sum(durations) / total if total > 0 else 0
        last_run = durations[-1] if durations else 0

        print(f"Total Run    : {total}")
        print(f"Avg Duration : {round(avg_duration,2)} sec")
        print(f"Last Run     : {last_run} sec")

    print("="*40)