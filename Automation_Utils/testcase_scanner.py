import os

BASE_PATH = "Automation_TestCase"

SKIP_FOLDERS = {
    "__pycache__",
    ".git",
    ".venv",
    "node_modules"
}

def scan_testcases():
    mapping = {}

    for cob in os.listdir(BASE_PATH):

        # 🔥 skip folder tertentu
        if cob in SKIP_FOLDERS:
            continue

        cob_path = os.path.join(BASE_PATH, cob)

        if not os.path.isdir(cob_path):
            continue

        mapping[cob] = {}

        for modul in os.listdir(cob_path):

            # 🔥 skip folder tertentu
            if modul in SKIP_FOLDERS:
                continue

            modul_path = os.path.join(BASE_PATH, cob, modul)

            if not os.path.isdir(modul_path):
                continue

            files = []

            for file in os.listdir(modul_path):

                # skip __pycache__
                if file.startswith("__"):
                    continue

                if file.endswith(".py"):
                    files.append(file.replace(".py", ""))

            mapping[cob][modul] = files

    return mapping