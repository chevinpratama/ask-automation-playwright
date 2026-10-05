from pathlib import Path
import json


def load_config():
    base_dir = Path(__file__).resolve().parents[1]
    file_path = base_dir / "Automation_DataAccess" / "config.json"
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def load_accounts():
    return load_config()["accounts"]


def get_base_url():
    return load_config()["base_url"]


def get_alt_url():
    return load_config()["alt_url"]
