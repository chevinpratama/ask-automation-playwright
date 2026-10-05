import time
from datetime import datetime
import pytest

from Automation_Analyst.dashboard import save_result, show_dashboard
from Automation_Analyst.failure_analyzers import analyze_error


def pytest_runtest_setup(item):
    """
    Capture start time sebelum test dijalankan
    """
    item.start_time = time.time()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook untuk ambil hasil test (pass / fail)
    """
    outcome = yield
    report = outcome.get_result()

    # hanya proses saat fase eksekusi test
    if report.when == "call":

        end_time = time.time()
        start_time = getattr(item, "start_time", end_time)

        duration = round(end_time - start_time, 2)

        status = "Passed" if report.passed else "Not Passed"

        result = {
            "testcase": item.name,
            "status": status,
            "start_time": datetime.fromtimestamp(start_time).strftime("%d/%m/%Y %H:%M:%S"),
            "end_time": datetime.fromtimestamp(end_time).strftime("%d/%m/%Y %H:%M:%S"),
            "duration": duration
        }

        # 🔥 kalau gagal → analisa error
        if report.failed:
            try:
                error_message = str(report.longrepr)
                error_info = analyze_error(error_message)
                result.update(error_info)
            except Exception as e:
                result.update({
                    "type": "Analyzer Error",
                    "root_cause": str(e),
                    "category": "Framework Issue",
                    "severity": "Low",
                    "solution": "Periksa module analyzer"
                })

        # 🔥 simpan & tampilkan
        try:
            save_result(result)
        except Exception as e:
            print(f"[ERROR] Gagal save result: {e}")

        try:
            show_dashboard(result)
        except Exception as e:
            print(f"[ERROR] Gagal tampilkan dashboard: {e}")
