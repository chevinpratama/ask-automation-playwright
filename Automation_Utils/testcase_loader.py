import importlib


def load_function(cob, modul, case_name):
    module_path = f"Automation_TestCase.{cob}.{modul}.{case_name}"
    module = importlib.import_module(module_path)

    # =========================
    # PRIORITAS 1: run_<nama_file>
    # =========================
    exact_run = f"run_{case_name}"
    if hasattr(module, exact_run):
        return getattr(module, exact_run)

    # =========================
    # PRIORITAS 2: test_<nama_file>
    # =========================
    exact_test = f"test_{case_name}"
    if hasattr(module, exact_test):
        return getattr(module, exact_test)

    # =========================
    # PRIORITAS 3: cari semua run_*
    # =========================
    for attr in dir(module):
        if attr.startswith("run_") and callable(getattr(module, attr)):
            return getattr(module, attr)

    # =========================
    # PRIORITAS 4: cari semua test_*
    # =========================
    for attr in dir(module):
        if attr.startswith("test_") and callable(getattr(module, attr)):
            return getattr(module, attr)

    # =========================
    # PRIORITAS 5: fallback run()
    # =========================
    if hasattr(module, "run"):
        return getattr(module, "run")

    # =========================
    # ERROR
    # =========================
    raise AttributeError(
        f"Tidak ditemukan function runner di module {module_path}"
    )
